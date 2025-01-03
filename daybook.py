#!/usr/bin/python3
from datetime import datetime
from time import time
from json import load, dump
from argparse import ArgumentParser
from pathlib import Path
from re import sub
from textwrap import fill as word_wrap

class Formats:
    def __init__(self) -> None:
        self.year = "│{:^70}│\n├────┬─────────────────────────────────────────────────────────────────┤\n".format
        self.month = "│ {} │{:^65}│\n├────┴─────────────────────────┬───────────────────────────────────────┤\n".format # ┼
        self.day = "│{:^30}│{:^39}│\n├──────────┬───────────────────┴───────────────────────────────────────┤\n".format
        self.note = "│ {} │ {}│\n".format

    def format_note(self, note: str) -> None:
        note = word_wrap(note, 57).split("\n")
        return f" │\n│{' ':<10}│ ".join([f"{line:<57}" for line in note])

class Combiner:
    def __init__(self, filename: str) -> None:
        if filename == '':
            exit("--combine-file/-c filename is required.")
        self.maind = load(open(f"{Path().home()}/.daybook.json", "r", encoding = "utf-8"))
        self.otherd = load(open(filename, "r", encoding = "utf-8"))

        for year in self.otherd.keys():
            if year in self.maind.keys():
                for month in self.otherd[year].keys():
                    if month in self.maind[year].keys():
                        for day in self.otherd[year][month].keys():
                            if day in self.maind[year][month].keys():
                                for notes in self.otherd[year][month][day]:
                                    if notes not in self.maind[year][month][day]:
                                        self.maind[year][month][day].append(notes)
                                        self.maind[year][month][day].sort(key = lambda a: sub(r"\D", "", a[0]))
                            else:
                                self.maind[year][month][day] = self.otherd[year][month][day]
                    else:
                        self.maind[year][month] = self.otherd[year][month]
            else:
                self.maind[year] = self.otherd[year]
        dump(self.maind, open(f"{Path().home()}/.daybook.json", "w", encoding = "utf-8"))

class Reader(Formats):
    def __init__(self, daybook: str, write_file: bool = True, filename: str = "daybook.txt") -> None:
        super().__init__()

        if daybook == '':
            daybook = f"{Path().home()}/.daybook.json"

        self.file_ = None
        self.write_file = write_file
        if write_file:
            self.file_ = open(f"{Path().home()}/" + filename, "w", encoding = "utf-8")

        self.months = ["January", "February", "March", "April", "May", 
                       "June", "July", "August", "September", "October",
                       "November", "December"]

        self.data = load(open(daybook, "r", encoding = "utf-8"))
        self.format()

    def format(self) -> None:
        text = f"┌{'─':─^70}┐\n"
        print(f"┌{'─':─^70}┐", flush = True)

        years = self.data.keys()
        for year in enumerate(years):
            text += self.year(year[1] + " DayBook By ReYeS")
            print(self.year(year[1]), end = "", flush = True)

            months = self.data[year[1]].keys()
            for month in enumerate(months):
                text += self.month(month[1], self.months[int(month[1]) - 1])
                print(self.month(month[1], self.months[int(month[1]) - 1]), end = "", flush = True)

                days = self.data[year[1]][month[1]].keys()
                for day in enumerate(days):
                    text += self.day(day[1].split('-')[1], day[1].split('-')[0])
                    print(self.day(day[1].split('-')[1], day[1].split('-')[0]), end = "", flush = True)

                    notes_ = self.data[year[1]][month[1]][day[1]]
                    for notes in enumerate(notes_):
                        if notes[0] != len(notes_) - 1:
                            additional = f" │\n│{'-':-<10}│{'-':-<59}"
                        else:
                            additional = " "
                        text += self.note(notes[1][0], self.format_note(notes[1][1]) +\
                                    additional)
                        print(self.note(notes[1][0], self.format_note(notes[1][1]) +\
                                additional), end = "", flush = True)

                    if day[0] != len(days) - 1 and year[0] != len(years) - 1:
                        end = f"├{'─':─<10}┴{'─':─<19}┬{'─':─^39}┤\n"
                    elif day[0] != len(days) - 1 and year[0] == len(years) - 1:
                        end = f"├{'─':─<10}┴{'─':─<19}┬{'─':─^39}┤\n"
                    elif day[0] == len(days) - 1 and month[0] != len(months) - 1 and year[0] != len(years) - 1:
                        end = f"├{'─':─<4}┬{'─':─<5}┴{'─':─^59}┤\n"
                    elif day[0] == len(days) - 1 and year[0] != len(years) - 1:
                        end = f"├{'─':─<10}┴{'─':─^59}┤\n" # ┴
                    else:
                        end = ""
                    text += end
                    print(end, end = "", flush = True)

        # if text.strip().split("\n")[-1] == f"├{'─':─<10}┴{'─':─<19}┬{'─':─^39}┤":
            # text = '\n'.join(text.strip().split("\n")[0:-1]) +\
            #         f"\n└{'─':─^10}┴{'─':─^59}┘\n"
        text += f"└{'─':─^10}┴{'─':─<59}┘\n"
        print(f"└{'─':─^10}┴{'─':─<59}┘", flush = True)
        # else:
            # print(f"└{'─':─^10}┴{'─':─<59}┘") # print(f"└{'─':─^70}┘")
        if self.write_file:
            self.file_.write(text)
            self.file_.close()

class Writter:
    def __init__(self, daybook: str) -> None:
        if daybook == '':
            daybook = f"{Path().home()}/.daybook.json"

        try:
            self.data = load(open(daybook, "r", encoding = "utf-8"))
        except:
            self.data = {}
        time_ = datetime.fromtimestamp(time()).strftime
        day = time_("%d") + "-" + time_("%A")
        self.set_keys(time_, day)
        self.data[time_("%Y")][time_("%m")][day].append([time_("%H:%M:%S"), input("Whats your feeling? - ")])
        dump(self.data, open(daybook, "w", encoding = "utf-8"))
        # strftime("%H:%M:%S.%f %w-%d-%m-%Y  -%j  %a /%b /%W")
        #           09:08:28.30  1-14-11-2022-318 Mon/Nov/46

    def set_keys(self, time_: any, day: str) -> None:
        if time_("%Y") not in self.data.keys():
            self.data[time_("%Y")] = {}
        if time_("%m") not in self.data[time_("%Y")].keys():
            self.data[time_("%Y")][time_("%m")] = {}
        if day not in self.data[time_("%Y")][time_("%m")].keys():
            self.data[time_("%Y")][time_("%m")][day] = []

if __name__ == "__main__":
    parser = ArgumentParser(description = "Daybook by ReYeS")
    parser.add_argument("mode", help = "Daybook mode (Write/Read)", 
                        type = str,
                        choices = ["write", "read", "combine", 
                                   "w", "r", "c",
                                   "0", "1", "1"])
    parser.add_argument("--daybook-file", "--daybook", "-df", "-d",
                        help = "Path to daybook file. Combining will combine file from path with file from home folder of this user.",
                        type = str, dest = "combine", default = "")
    args = parser.parse_args()
    del parser

    if args.mode in ["read", "r", "1"]:
        Reader(args.combine)
    elif args.mode in ["write", "w", "0"]:
        Writter(args.combine)
    elif args.mode in ["combine", "c", "2"]:
        Combiner(args.combine)
