import datetime
import time
import sys
from numpy import linspace
import benchlib.argparsing as ap


def parse_settings_for_display(settings):
    data = {}
    max_length = 0
    action = {list: lambda a: " ".join(map(str, a)), str: str, int: str, bool: str}
    for k, v in settings.items():
        if v:
            data[str(k)] = action[type(v)](v)
            length = len(data[k])
            if length > max_length:
                max_length = length
    data["length"] = max_length
    return data


def calculate_duration(settings, tests):
    number_of_tests = len(tests) * settings["loops"]
    time_per_test = settings["runtime"]
    duration_in_seconds = number_of_tests * time_per_test
    duration = str(datetime.timedelta(seconds=duration_in_seconds))
    return duration


def display_header(settings, tests):
    header = "+++ Fio Benchmark Script +++"
    blockchar = "\u2588"
    data = parse_settings_for_display(settings)
    fl = 30  # Width of left column of text
    length = data["length"]
    width = length + fl - len(header)
    duration = calculate_duration(settings, tests)
    print(f"{blockchar}" * (fl + width))
    print((" " * int(width / 2)) + header)
    print()
    if settings["dry_run"]:
        print()
        print(" ====---> WARNING - DRY RUN <---==== ")
        print()
    estimated = "Estimated duration"
    print(f"{estimated:<{fl}}: {duration:<}")
    descriptions = ap.get_argument_description()
    for item in settings.keys():
        if item not in settings["filter_items"]:
            description = descriptions[item]
            if item in data.keys():
                print(f"{description:<{fl}}: {data[item]:<}")
            else:
                if settings[item]:
                    print(f"{description}:<{fl}: {settings[item]:<}")
    print()
    print(f"{blockchar}" * (fl + width))


def ProgressBar(iterObj):
    """https://stackoverflow.com/questions/3160699/python-progress-bar/49234284#49234284"""

    def SecToStr(sec):
        m, s = divmod(sec, 60)
        h, m = divmod(m, 60)
        return "%d:%02d:%02d" % (h, m, s)

    L = len(iterObj)
    steps = {
        int(x): y
        for x, y in zip(
            linspace(0, L, min(100, L), endpoint=False),
            linspace(0, 100, min(100, L), endpoint=False),
        )
    }
    # quarter and half block chars
    qSteps = ["", "\u258E", "\u258C", "\u258A"]
    startT = time.time()
    timeStr = "   [0:00:00, -:--:--]"
    activity = [" -", " \\", " |", " /"]
    for nn, item in enumerate(iterObj):
        if nn in steps:
            done = "\u2588" * int(steps[nn] / 4.0) + qSteps[int(steps[nn] % 4)]
            todo = " " * (25 - len(done))
            barStr = "%4d%% |%s%s|" % (steps[nn], done, todo)
        if nn > 0:
            endT = time.time()
            timeStr = " [%s, %s]" % (
                SecToStr(endT - startT),
                SecToStr((endT - startT) * (L / float(nn) - 1)),
            )
        sys.stdout.write("\r" + barStr + activity[nn % 4] + timeStr)
        sys.stdout.flush()
        yield item
    barStr = "%4d%% |%s|" % (100, "\u2588" * 25)
    timeStr = "   [%s, 0:00:00]\n" % (SecToStr(time.time() - startT))
    sys.stdout.write("\r" + barStr + timeStr)
    sys.stdout.flush()
