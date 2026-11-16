#!/usr/bin/env python3
"""Runs shell steps side by side and reports them together; .claude/check.sh hands it every check of the repo.

    python3 -I .claude/run_steps.py [--budget SECONDS] [--step-budget SECONDS] NAME::COMMAND [NAME::COMMAND ...]

A step is a name and one shell command line (run with `bash -c` from the current folder), joined by `::`. Every step
starts at once and runs whatever the others do. Each step keeps its own output: a step that passed shows one line (its last
line of output), one that failed shows all of it after the list, so the tail is the error. The exit code is 1 when any
step failed, and the last lines name them.

--step-budget SECONDS (else $CHECK_STEP_BUDGET_SECONDS) fails a step that runs longer than that, and --budget SECONDS (else
$CHECK_BUDGET_SECONDS) fails the whole run past that time. A step over its budget is killed with everything it started
and named in the report. A budget is a limit, not a retry or a longer wait.

Python 3.9+, standard library only.
"""

import argparse
import contextlib
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time

sys.dont_write_bytecode = True

POLL_SECONDS = 0.02


class Step:
    def __init__(self, index, name, command, base):
        self.name = name
        self.command = command
        self.output = os.path.join(base, "out-%d.txt" % index)
        self.proc = None
        self.started = self.seconds = self.code = None
        self.reason = ""  # set when the step was killed over a budget

    def start(self):
        with open(self.output, "wb") as out:
            # Its own session, so that killing the step reaches everything it started.
            self.proc = subprocess.Popen(
                ["bash", "-c", self.command],
                stdin=subprocess.DEVNULL,
                stdout=out,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
        self.started = time.monotonic()

    def kill(self, reason):
        self.reason = reason
        with contextlib.suppress(ProcessLookupError):
            os.killpg(self.proc.pid, signal.SIGKILL)

    def finish(self):
        self.proc.wait()
        self.seconds = time.monotonic() - self.started
        self.code = self.proc.returncode

    @property
    def failed(self):
        return self.proc is None or self.code != 0 or bool(self.reason)

    @property
    def why(self):
        if self.proc is None:
            return "never started: the run was over"
        return self.reason or "exit %s" % self.code

    def text(self):
        with open(self.output, "rb") as f:
            return f.read().decode("utf-8", "replace").strip()


def say(text=""):
    print(text, flush=True)


def finished_line(step):
    last = step.text().splitlines()[-1].strip() if step.text() else ""
    return "%s %6.1fs  %s%s" % (
        "FAIL" if step.failed else "  ok",
        step.seconds,
        step.name,
        "" if step.failed or not last else "  -> " + last,
    )


def run(steps, budget, step_budget):
    """Runs the steps and prints the report; returns the exit code."""
    running = list(steps)
    began = time.monotonic()
    try:
        for step in steps:
            step.start()
        while running:
            now = time.monotonic()
            for step in list(running):
                if step.proc.poll() is None:
                    if budget and now - began > budget:
                        step.kill("still running when the run passed its budget of %gs" % budget)
                    elif step_budget and now - step.started > step_budget:
                        step.kill("over its budget of %gs" % step_budget)
                if step.proc.poll() is not None:
                    step.finish()
                    running.remove(step)
                    say(finished_line(step))
            time.sleep(POLL_SECONDS)
    finally:  # interrupted: whatever still runs is stopped
        for step in running:
            step.kill("stopped: the run was interrupted")
            step.finish()
            say(finished_line(step))
    return report(steps, time.monotonic() - began)


def report(steps, elapsed):
    failed = [s for s in steps if s.failed]
    for step in failed:
        say("\n---- FAILED (%s, %.1fs): %s ----" % (step.why, step.seconds, step.name))
        if step.text():
            say(step.text())
    if failed:
        say("\nFAILED %d of %d steps in %.1fs:" % (len(failed), len(steps), elapsed))
        for step in failed:
            say("  %s (%s)" % (step.name, step.why))
            if os.environ.get("GITHUB_ACTIONS") == "true":
                say("::error title=%s::%s" % (step.name, step.why))
        return 1
    work = sum(s.seconds for s in steps)
    say("\n%d steps passed in %.1fs (%.1fs of work, side by side)" % (len(steps), elapsed, work))
    return 0


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--budget", type=float, default=float(os.environ.get("CHECK_BUDGET_SECONDS") or 0))
    parser.add_argument("--step-budget", type=float, default=float(os.environ.get("CHECK_STEP_BUDGET_SECONDS") or 0))
    parser.add_argument("steps", nargs="+", metavar="NAME::COMMAND")
    args = parser.parse_args(argv)
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(143))  # let `finally` kill the steps
    base = tempfile.mkdtemp(prefix="run-steps-")
    try:
        steps = []
        for i, text in enumerate(args.steps):
            name, sep, command = text.partition("::")
            if not sep:
                parser.error("a step is NAME::COMMAND, got: %s" % text)
            steps.append(Step(i, name, command, base))
        return run(steps, args.budget, args.step_budget)
    finally:
        shutil.rmtree(base, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
