/*
 * Timer.hpp
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

#ifndef __COMBINA_TIMER_HPP
#define __COMBINA_TIMER_HPP

#include <chrono>
#include <cstddef>


/**
 * \brief Abstract base class for timers.
 *
 * Timers can be derived from a variety of clocks. Every timer has an internal
 * accumulator that accumulates the duration for which the timer has been
 * running according to its underlying clock.
 */
class TimerBase {
protected:
    bool _running;              ///< Indicates whether the timer is active.

public:
    TimerBase() : _running(false) {}
    TimerBase(const TimerBase& timer) : _running(timer._running) {}
    virtual ~TimerBase() {}

    bool is_running() const { return _running; }    ///< Indicates whether the timer is currently running.

    virtual void start() = 0;           ///< Activates the timer.
    virtual void stop() = 0;            ///< Deactivates the timer.
    virtual void reset() = 0;           ///< Resets the accumulated time to zero.
    virtual double secs() const = 0;    ///< Returns total number of accumulated seconds.
};


template <class Clock> class ChronoTimer : public TimerBase {
public:
    typedef typename Clock::time_point time_point_type;
    typedef typename Clock::duration duration_type;

private:
    Clock _clock;
    duration_type _acc;
    time_point_type _start;

public:
    ChronoTimer() {}
    explicit ChronoTimer(const Clock& clock) : _clock(clock), _acc(), _start() {}
    ChronoTimer(const ChronoTimer<Clock>& timer) : TimerBase(timer), _clock(timer._clock), _acc(timer._acc), _start(timer._start) {}

    virtual void start() {
        if(!_running) {
            _running = true;
            _start = _clock.now();
        }
    }

    virtual void stop() {
        if(_running) {
            _acc += _clock.now() - _start;
            _running = false;
        }
    }

    virtual void reset() {
        _acc = duration_type::zero();
        if(_running) {
            _start = _clock.now();
        }
    }

    virtual double secs() const {
        duration_type dur = _acc;
        if(_running) {
            dur += _clock.now() - _start;
        }
        return std::chrono::duration_cast<std::chrono::duration<double>>(dur).count();
    }
};

#endif /* end of include guard: __COMBINA_TIMER_HPP */
