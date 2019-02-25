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

#ifndef __COMBINA_VBC_MONITOR_HPP
#define __COMBINA_VBC_MONITOR_HPP

#include <config.hpp>
#include "../combina_fwd.hpp"
#include "../Monitor.hpp"

#include <iostream>
#include <string>
#include <unordered_set>


/**
 * \brief Monitor class recording VBC files.
 *
 * VBC is a file format developed by Sebastian Leipert at the University of
 * Cologne for recording and visualizing branch-and-bound trees. This monitor
 * class uses monitoring data provided by the Combina solver to produce a VBC
 * file representing the branch-and-bound tree explored by Combina.
 *
 * VBC files can include information on the timing of certain events. VbcMonitor
 * uses an internal ChronoTimer using the system's steady clock to measure this
 * timing information if requested. The timer is started at the beginning of the
 * search and stopped at its end. It is reset on every restart. Because Combina
 * processes nodes very quickly and VBC only allows timing precise to a hundreth
 * of a second, an optional time dilation factor can be specified. All time
 * measurements are internally multiplied with the time dilation factor before
 * being recorded.
 */
class VbcMonitor : public MonitorBase {
public:
    enum class Compression {
        none = 0,
        bzip2 = 1,
        gzip = 2,
    };

private:
    bool timing_;       ///< Indicates whether timing information is recorded.
    double dilate_;     ///< Factor by which time is dilated.
    TimerPtr timer_;    ///< Timer used for timing.
    Compression compr_; ///< Type of compression.

    std::string path_;                      ///< Path of output file.
    std::ostream out_;                      ///< Output stream.
    std::unique_ptr<std::streambuf> buf_;   ///< Output stream buffer.

    std::unordered_set<size_t> cat_;    ///< Set of uncategorized nodes.

public:
    VbcMonitor(CombinaBnBSolver* solver, const std::string& path, bool timing = true);
    VbcMonitor(const VbcMonitor&) = delete;
    VbcMonitor(VbcMonitor&&) = delete;
    virtual ~VbcMonitor();

    bool has_timing() const { return timing_; }                 ///< Indicates whether timing is recorded.
    void set_timing(bool timing) { timing_ = timing; }          ///< Sets the timing flag.
    double get_time_dilation() const { return dilate_; }        ///< Returns the time dilation factor.
    void set_time_dilation(double dilate) { dilate_ = dilate; } ///< Sets the time dilation factor.
    Compression get_compression() const { return compr_; }      ///< Returns current compression method.

    virtual void on_start_search();
    virtual void on_create(const NodePtr& node);
    virtual void on_select(const NodePtr& node);
    virtual void on_change(const NodePtr& node, NodeState state);
    virtual void on_stop_search();
};

#endif /* end of include guard: __COMBINA_VBC_MONITOR_HPP */
