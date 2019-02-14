/*
 * monitors/VbcMonitor.hpp
 *
 * This file is part of pycombina.
 *
 * Copyright 2017-2018 Adrian Bürger, Clemens Zeile, Sebastian Sager, Moritz Diehl
 *
 * pycombina is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * pycombina is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with pycombina. If not, see <http://www.gnu.org/licenses/>.
 *
 */

#include <chrono>
#include <iomanip>
#include <map>
#include <memory>
#include <sstream>

#include <pybind11/pybind11.h>

#include "VbcMonitor.hpp"
#include "../Node.hpp"
#include "../Timer.hpp"

namespace py = pybind11;


#ifdef COMBINA_VBC_USE_BOOST
#include <boost/iostreams/filtering_streambuf.hpp>
#include <boost/iostreams/device/file.hpp>
#include <boost/iostreams/filter/bzip2.hpp>
#include <boost/iostreams/filter/gzip.hpp>

namespace bio = boost::iostreams;


static std::unique_ptr<std::streambuf> create_buffer() {
    return std::make_unique<bio::filtering_ostreambuf>();
}


static void open_file(std::ostream& stream, std::string path, VbcMonitor::Compression compr) {
    using pybind11::operator""_a;

    bio::filtering_ostreambuf* streambuf = reinterpret_cast<bio::filtering_ostreambuf*>(stream.rdbuf());

    // close prior file sinks and reset the device
    if(streambuf->is_complete()) {
        streambuf->pop();
    }
    streambuf->reset();
    stream.clear();

    // install a compression filter
    switch(compr) {
    case VbcMonitor::Compression::bzip2:
        if(path.size() < 4 || !std::equal(path.cbegin() + (path.size() - 4), path.cend(), ".bz2")) {
            path = path + ".bz2";
        }
        streambuf->push(bio::bzip2_compressor());
        break;
    case VbcMonitor::Compression::gzip:
        if(path.size() < 3 || !std::equal(path.cbegin() + (path.size() - 3), path.cend(), ".gz")) {
            path = path + ".gz";
        }
        streambuf->push(bio::gzip_compressor());
        break;
    case VbcMonitor::Compression::none:
        break;
    }

    // open file sink
    bio::file_sink file(path);
    if(file.is_open()) {
        streambuf->push(file);
        assert(streambuf->is_complete());
    }
    else {
        py::gil_scoped_acquire lock;
        py::print("WARNING: failed to open VBC file for output", "file"_a=py::module::import("sys").attr("stderr"));
        return;
    }
}


static void close_file(std::ostream& stream) {
    bio::filtering_ostreambuf* streambuf = reinterpret_cast<bio::filtering_ostreambuf*>(stream.rdbuf());

    if(streambuf->is_complete()) {
        streambuf->pop();
    }
}
#else
#include <fstream>

static std::unique_ptr<std::streambuf> create_buffer() {
    return std::make_unique<std::filebuf>();
}


static void open_file(std::ostream& stream, std::string path, VbcMonitor::Compression compr) {
    using pybind11::operator""_a;

    std::filebuf* streambuf = reinterpret_cast<std::filebuf*>(stream.rdbuf());

    // close prior file sinks and reset the device
    streambuf->close();
    stream.clear();

    // install a compression filter
    if(compr != VbcMonitor::Compression::none) {
        py::gil_scoped_acquire lock;
        py::print("WARNING: pycombina was built without compression capability", "file"_a=py::module::import("sys").attr("stderr"));
        return;
    }

    // open file sink
    streambuf->open(path, std::ios_base::out);
    if(!streambuf->is_open()) {
        py::gil_scoped_acquire lock;
        py::print("WARNING: failed to open VBC file for output", "file"_a=py::module::import("sys").attr("stderr"));
        return;
    }
}


static void close_file(std::ostream& stream) {
    std::filebuf* streambuf = reinterpret_cast<std::filebuf*>(stream.rdbuf());
    streambuf->close();
}
#endif

// color code table for node states (adopted from Minotaur)
static const unsigned int color_codes[] = {
    4,  // NODE_ACTIVE
    8,  // NODE_SELECTED
    6,  // NODE_FATHOMED
    13, // NODE_INFEASIBLE
    9,  // NODE_SOLVED
    2,  // NODE_INTEGER
};


// macro determining whether node state is terminal
#define NODE_STATE_TERMINAL(x) (x >= NODE_FATHOMED)


// informative message for each status
static const char* const status_messages[] = {
    nullptr,                    // NODE_ACTIVE
    nullptr,                    // NODE_SELECTED
    "fathomed by upper bound",  // NODE_FATHOMED
    "no feasible children",     // NODE_INFEASIBLE
    "branching performed",      // NODE_SOLVED
    "solution found",           // NODE_INTEGER
};


// lookup table for file extensions and compression methods
static const std::map<std::string, VbcMonitor::Compression> compression_table {
    { ".bz2", VbcMonitor::Compression::bzip2 },
    { ".gz", VbcMonitor::Compression::gzip }
};


static VbcMonitor::Compression infer_compression_method(const std::string& path) {
    for(const auto& entry : compression_table) {
        size_t suffix_size = entry.first.size();
        if(path.size() >= suffix_size && std::equal(path.cbegin() + (path.size() - suffix_size), path.cend(), entry.first.cbegin())) {
            return entry.second;
        }
    }
    return VbcMonitor::Compression::none;
}


static std::string vbc_clock_string(double timestamp) {
    std::ostringstream str;
    int hours, minutes;
    double seconds;

    hours = (int)std::trunc(timestamp / 3600);
    minutes = (int)std::trunc(fmod(timestamp, 3600) / 60);
    seconds = fmod(timestamp, 60);

    str.fill('0');
    str.precision(2);
    str << std::setw(2) << hours << ':'
        << std::setw(2) << minutes << ':'
        << std::setw(5) << std::fixed << seconds;

    return str.str();
}


VbcMonitor::VbcMonitor(CombinaBnBSolver* solver, const std::string& path, bool timing)
    : MonitorBase(solver),
      timing_(timing),
      dilate_(1.0),
      timer_(nullptr),
      path_(path),
      out_(nullptr),
      buf_(create_buffer()),
      cat_()
{
    out_.rdbuf(buf_.get());
}


VbcMonitor::~VbcMonitor() {}


void VbcMonitor::on_start_search() {
    // infer compression method from path
    compr_ = infer_compression_method(path_);

    // attempt to open file
    open_file(out_, path_, compr_);

    // write file header
    out_ << "#TYPE: COMPLETE TREE" << std::endl
         << "#TIME: " << (timing_ ? "SET" : "NOT") << std::endl
         << "#BOUNDS: " << (timing_ ? "SET" : "NONE") << std::endl
         << "#INFORMATION: STANDARD" << std::endl
         << "#NODE_NUMBER: NONE" << std::endl;

    // create fake root node to satisfy VBC's need for a single root
    if(timing_) {
        out_ << "00:00:00.00 N 0 1 " << color_codes[NODE_SOLVED] << std::endl
             << "00:00:00.00 I 1 \\ivirtual root node" << std::endl;
    }
    else {
        out_ << "n 1 \\ivirtual root node" << std::endl;
    }

    // start timer
    if(timing_) {
        if(!timer_) {
            timer_ = std::make_shared<ChronoTimer<std::chrono::steady_clock>>();
        }
        timer_->reset();
        timer_->start();
    }

    // clear the uncategorized set
    cat_.clear();
}


void VbcMonitor::on_create(Node* node) {
    size_t node_num, parent_num;
    std::string clock_str;

    if(out_) {
        node_num = node->get_seq_num() + 2;
        parent_num = node->get_parent() ? node->get_parent()->get_seq_num() + 2 : 1;

        if(timing_) {
            clock_str = vbc_clock_string(timer_->secs() * dilate_);

            out_ << clock_str << " N " << parent_num << ' ' << node_num << ' ' << color_codes[NODE_ACTIVE] << '\n'
                 << clock_str << " I " << node_num << ' '
                 << "\\inode " << node->get_seq_num()
                 << "\\nlower bound: " << node->get_lb()
                 << "\\idepth:          " << node->get_depth()
                 << "\\nactive control: " << node->get_b_active()
                 << std::endl;
        }
        else {
            out_ << "n " << node_num << " \\inode " << node->get_seq_num()
                 << "\\nlower bound: " << node->get_lb()
                 << "\\idepth           " << node->get_depth()
                 << "\\nactive control: " << node->get_b_active()
                 << "\ne " << parent_num << ' ' << node_num
                 << std::endl;
            cat_.insert(node_num);
        }
    }
}


void VbcMonitor::on_select(Node* node) {
    this->on_change(node, NODE_SELECTED);
}


void VbcMonitor::on_change(Node* node, NodeState state) {
    size_t node_num;
    unsigned int color_code;
    const char* status_msg;
    std::string clock_str;

    if(out_) {
        // determine VBC node number
        node_num = node->get_seq_num() + 2;

        // determine color code and status message
        color_code = color_codes[state];
        status_msg = status_messages[state];

        if(timing_) {
            // generate clock string
            clock_str = vbc_clock_string(timer_->secs() * dilate_);
            
            // write color update, information string extension, and upper bound update
            out_ << clock_str << " P " << node_num << ' ' << color_code << '\n';
            if(status_msg) {
                out_ << clock_str << " A " << node_num << "\\i\\i\\n" << status_msg << '\n';
            }
            if(state == NODE_INTEGER) {
                out_ << clock_str << " U " << node->get_lb() << '\n';
            }
            out_.flush();
        }
        else if(NODE_STATE_TERMINAL(state)) {
            // write category code
            out_ << "c " << node_num << ' ' << color_code << std::endl;

            // node is no longer uncategorized
            cat_.erase(node_num);
        }
    }
}


void VbcMonitor::on_stop_search() {
    // stop timer if necessary
    if(timer_) {
        timer_->stop();
    }

    // categorize remaining uncategorized nodes as active
    if(out_ && !timing_ && !cat_.empty()) {
        for(size_t node_num : cat_) {
            out_ << "c " << node_num << ' ' << color_codes[NODE_ACTIVE] << '\n';
        }
        out_.flush();
    }
    cat_.clear();

    // close output file
    close_file(out_);
}
