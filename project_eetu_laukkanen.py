# Eetu Laukkanen, eetu.laukkanen@student.tut.fi
# Opiskelijanumero: 274850
# Status: READY
# TIE-02100 Johdatus ohjelmointiin
# Eetu Laukkanen, eetu.laukkanen@student.tut.fi
# Student number: 274850
# Status: READY

"""
KUVAUS:

Ohjelma on erään pelin munkki luokan ensimmöisen asteen
kyky-simulaattori. Tarkoituksena on, että käyttäjä voi asetta haluamansa
hahmon tason (Character level) ja sen jälkeen asettaa kyky pisteitä
(skill points) eri kykyihin + ja - napeilla. Näin voi testata, mihin
kaikkeen pisteet tietyllä hahmon tasolla riittävät. Ymmärtääkseni
ohjelma vastaa skaalautuvaa projektia.
"""

from tkinter import *
# Determines the file with skill information.
SKILLFILE = "skillfile.txt"
# Determines the directory in which the used images are stored.
PHOTODIRECTORY = "ingifs"
# The largest cost of upgrading skill possible.
MOST_SKILL_POINTS_POSSIBLY_REQUIRED = 20


def read_input_file(file_to_read):
    """ Read's a file

    :param file_to_read: name of a text file in current directory that
    stores the skill information. Each row in file has to be of form:
    skill name;skill attack values for each level separated by a "," or
    "-" if the skill doesn't have them;prerequisite skill name and that
    skill's required skill level separated by a "," or "-" if there is
    no prerequisite;amount of skill points required to upgrade the skill
    ;required character levels for each skill level separated by a ",";
    Skills description, if there are values that change with the skills
    level with in said description, they have to be replaced by "{}" and
    be added after the description, one for each level of the skill.;
    file name of the skills icon image;Column value, which column should
    the skill be placed in on the skill tree;Row value, which row should
    the skill be placed in on the skill tree.
    :return: dict or str.  If reading the file was successful returns
    dict, keys are skill names and values the corresponding object of
    class Skill. If there was an error reading the file a error text
    describing what happened is returned.
    """
    error = False

    try:
        file_ = open(file_to_read)
    except OSError:
        error = True
        error_text = "Couldn't find " + SKILLFILE

    # If there are no errors, each row of the file is used to create
    # a Skill object and then stored into skill_dict
    if not error:
        try:
            skill_dict = {}
            for row in file_:
                (name, attack, prerequisite, points_to_up, lvl_req,
                 description, icon_file_name, grid_column,
                 grid_row) = row.strip().split(";")

                # Makes sure the icon file is right by trying to open it
                try:
                    open(PHOTODIRECTORY + "/" + icon_file_name)
                except OSError:
                    error = True
                    error_text = ("Couldn't find " + icon_file_name +
                                  " in " + PHOTODIRECTORY)
                    break

                lvl_req = lvl_req.split(",")
                lvl_req = [int(i) for i in lvl_req]
                (prereq_skill_name,
                 *prereq_skill_lvl) = prerequisite.split(",")
                if prereq_skill_name != "-":
                    prereq_skill_lvl = int(prereq_skill_lvl[0])
                attack = attack.split(",")
                description = description.split(",")

                skill_dict[name] = Skill(name, attack,
                                         prereq_skill_name,
                                         prereq_skill_lvl,
                                         int(points_to_up),
                                         lvl_req, description,
                                         icon_file_name,
                                         int(grid_column),
                                         int(grid_row))

        except ValueError:
            error = True
            error_text = SKILLFILE + " corrupted"

    if not error:
        for skill_string in skill_dict:
            skill = skill_dict[skill_string]
            if skill.prereq_skill_name not in skill_dict \
                    and skill.prereq_skill_name != "-":
                error = True
                error_text = SKILLFILE + " corrupted"
                break

    if error:
        return error_text
    else:
        return skill_dict


class Skill:
    def __init__(self, name, attack, prereq_skill_name,
                 prereq_skill_lvl, points_to_up, lvl_req, description,
                 icon_file_name, grid_column, grid_row):
        """Class used to store information about each skill
        :param name: str, skill's name
        :param attack: str, values associated with the skill's attack,
        or "-" if the skill has no such values.
        :param prereq_skill_name: str, name of the prerequisite skill
        if there is one, otherwise "-"
        :param prereq_skill_lvl: int, required level of the prerequisite
        skill if there is one, otherwise empty list.
        :param points_to_up: int, skill points required to upgrade skill
        :param lvl_req: list, each value is the character level required
        for corresponding skill level. For example value in index 0 is
        the character level required for skill level 1, and so on.
        List length must be 5.
        :param description: list, first value is the general description
        of what the skill does in a string. If something in the general
        description changes with skill level, that part is marked with
        "{}". Subsequent values are then used with the format function
        to determine what the description should say at that level.
        Descriptions can have two such changing parts. Length of the
        list MUST be either 1 (if there are no changing parts), 6
        (if there is one changing part) or 11 (if there are two
        changing parts).
        :param icon_file_name: string, name of the skill's icon.
        :param grid_column: int, column in which the skill
        (specifically it's icon) should be placed.
        :param grid_row: int, row in which the skill (specifically it's
         icon) should be placed.
        """

        self.name = name
        self.attack = attack
        self.prereq_skill_name = prereq_skill_name
        self.prereq_skill_lvl = prereq_skill_lvl
        self.points_to_up = points_to_up
        self.lvl_req = lvl_req  # A list, lvl req. for each skill level.
        self.description = description
        self.icon_file_name = icon_file_name
        self.icon_file = PhotoImage(
            file=PHOTODIRECTORY + "/" + icon_file_name)
        self.grid_column = int(grid_column)
        # Add one to leave room for character info entries.
        self.grid_row = int(grid_row) + 1
        self.skill_level = 0
        self.skill_max_level = 5


class SkillTree:

    def __init__(self):
        self.__window = Tk()
        self.__window.title("Monk skills")
        self.__window.grid_columnconfigure(0, weight=1)
        self.__window.grid_rowconfigure(0, weight=1)

        self.__char_lvl_text = Label(text="Enter Character level:")
        self.__char_lvl_text.grid(column=1, row=0, columnspan=3)

        self.__stop_button = Button(text="stop", command=self.stop)
        self.__stop_button.grid(column=14, row=13)

        self.__skills = read_input_file(SKILLFILE)

        # If there was an error reading the skill data file, an error
        # is given and nothing else happens.
        if type(self.__skills) == str:
            self.__char_lvl_text.configure(text=self.__skills)

        else:
            # Traces character level to update it when ever the user
            # changes it
            self.__char_lvl_tracer = StringVar()
            self.__char_lvl = Entry(
                textvariable=self.__char_lvl_tracer, width=3)
            self.__char_lvl.grid(column=4, row=0)
            self.__char_lvl.insert(0, "20")
            self.__char_lvl_tracer.trace(
                "w", lambda name, index, mode: self.change_level())

            self.__skill_points = 10 + 20 * (
                int(self.__char_lvl.get()) - 1)
            self.__skill_points_indicator = Label(
                text="Available skillpoints: " + str(
                    self.__skill_points))
            self.__skill_points_indicator.grid(
                column=5, row=0, columnspan=7)

            self.__reset_button = Button(
                text="reset", command=self.reset_all)
            self.__reset_button.grid(column=13, row=13)

            self.__skills = read_input_file(SKILLFILE)

            self.__skills_ui_elem_ALL = {}  # Stores UI elements
            # Creates the icon and necessary buttons for all skills.
            for skill in self.__skills:

                self.__skill_ui_elem = {}
                self.__icon_label = Label(
                    image=self.__skills[skill].icon_file, height=50,
                    width=50)
                self.__icon_label.grid(
                    column=self.__skills[skill].grid_column,
                    row=self.__skills[skill].grid_row)

                # When mousing over a skill icon, it's information
                # is shown on the info box.
                self.__icon_label.bind(
                    "<Enter>", lambda event, x=skill:
                    self.update_skill_info_box(x))
                self.__skill_ui_elem["icon"] = self.__icon_label

                self.__skill_lvl_indicator = Label(
                    text=str(self.__skills[skill].skill_level) + "/5")
                self.__skill_lvl_indicator.grid(
                    column=self.__skills[skill].grid_column,
                    row=self.__skills[skill].grid_row + 1, sticky="S")
                self.__skill_ui_elem["lvl_indicator"] = (
                    self.__skill_lvl_indicator)

                self.__upgrade_skill_button = Button(
                    text="+", bg="green",
                    command=lambda x=skill: self.upgrade_skill(x))
                self.__upgrade_skill_button.grid(
                    column=self.__skills[skill].grid_column + 1,
                    row=self.__skills[skill].grid_row,
                    sticky="NW")
                self.__skill_ui_elem["up"] = self.__upgrade_skill_button

                self.__downgrade_skill_button = Button(
                    text="-", bg="gray",
                    command=lambda x=skill: self.downgrade_skill(x),
                    state=DISABLED)
                self.__downgrade_skill_button.grid(
                    column=self.__skills[skill].grid_column + 1,
                    row=self.__skills[skill].grid_row, sticky="SW")
                self.__skill_ui_elem["down"] = (
                    self.__downgrade_skill_button)

                self.__skills_ui_elem_ALL[skill] = self.__skill_ui_elem

                self.check_skill_requirements(skill)

            # Prerequisite indicating arrows
            self.__right_down_short_arrow = PhotoImage(
                file=PHOTODIRECTORY + "/" +
                     "arrow_right_down_short.gif")
            self.__right_down_short_arrow_label = Label(
                image=self.__right_down_short_arrow)
            self.__right_down_short_arrow_label.grid(
                row=2, column=14, columnspan=2, rowspan=2)

            self.__left_down_short_arrow = PhotoImage(
                file=PHOTODIRECTORY + "/" + "arrow_left_down_short.gif")
            self.__left_down_short_arrow_label = Label(
                image=self.__left_down_short_arrow)
            self.__left_down_short_arrow_label.grid(
                row=8, column=1, columnspan=2, rowspan=2)

            self.__left_down_long_arrow = PhotoImage(
                file=PHOTODIRECTORY + "/" + "arrow_left_down_long.gif")
            self.__left_down_long_arrow_label = Label(
                image=self.__left_down_long_arrow)
            self.__left_down_long_arrow_label.grid(
                row=2, column=10, rowspan=4, columnspan=2)

            self.__right_down_long_arrow = PhotoImage(
                file=PHOTODIRECTORY + "/" + "arrow_right_down_long.gif")
            self.__right_down_long_arrow_label = Label(
                image=self.__right_down_long_arrow)
            self.__right_down_long_arrow_label.grid(
                row=8, column=5, rowspan=4, columnspan=2)

            self.__down_long_arrow = PhotoImage(
                file=PHOTODIRECTORY + "/" + "arrow_down_long.gif")
            self.__down_long_arrow_label = Label(
                image=self.__down_long_arrow)
            self.__down_long_arrow_label.grid(
                row=7, column=11, rowspan=3)

            self.__short_arrow_placements = ([3, 6], [5, 6], [5, 13])
            self.__down_short_arrow = PhotoImage(
                file=PHOTODIRECTORY + "/" + "arrow_down_short.gif")
            for i in self.__short_arrow_placements:
                self.__down_short_arrow_label = Label(
                    image=self.__down_short_arrow)
                self.__down_short_arrow_label.grid(
                    row=i[0], column=i[1])

            # Widgets for skill info panel
            self.__skill_info_text_label = Label(
                text="Skill info", width=40)
            self.__skill_info_text_label.grid(
                column=16, row=0, sticky=S, columnspan=2)
            self.__skill_info_name = Label()
            self.__skill_info_name.grid(column=16, row=1, columnspan=2)

            self.__skill_info_attack_label = Label(
                text="Skill attack values: ")
            self.__skill_info_attack_label.grid(
                column=16, row=2, sticky=W, padx=5)
            self.__skill_info_attack = Label()
            self.__skill_info_attack.grid(column=17, row=2, sticky=W)

            self.__skill_info_prerequisite_label = Label(
                text="Prerequisite skill: ")
            self.__skill_info_prerequisite_label.grid(
                column=16, row=3, sticky=W, padx=5)
            self.__skill_info_prerequisite = Label()
            self.__skill_info_prerequisite.grid(
                column=17, row=3, sticky=W, columnspan=3)

            self.__skill_info_points_to_up_label = Label(
                text="Points to upgrade: ")
            self.__skill_info_points_to_up_label.grid(
                column=16, row=4, sticky=W, padx=5)
            self.__skill_info_points_to_up = Label()
            self.__skill_info_points_to_up.grid(
                column=17, row=4, sticky=W)

            self.__skill_info_level_requirements_label = Label(
                text="Level requirement: ")
            self.__skill_info_level_requirements_label.grid(
                column=16, row=5, sticky=W, padx=5)
            self.__skill_info_level_requirements = Label()
            self.__skill_info_level_requirements.grid(
                column=17, row=5, sticky=W)

            self.__skill_info_description = Label(wraplength=250)
            self.__skill_info_description.grid(
                column=16, row=6, columnspan=2, sticky=W, padx=5)

    def update_skill_info_box(self, skill_string):
        """Function used to display information about a skill as user
        hovers over it's icon. Tied to each skills icon label with
        "bind".
        :param skill_string: Name of the skill that the user is
        hovering over.
        :return: NONE
        """
        skill = self.__skills[skill_string]

        # When a skill is at lvl 0, information about it shown as if it
        # was level 1. Used below.
        if skill.skill_level == 0:
            display_skill_level = "1"
        else:
            display_skill_level = str(skill.skill_level)

        self.__skill_info_name.configure(
            text=skill.name + " Lvl. " + display_skill_level)

        # If there is no prerequisite skill.
        if skill.prereq_skill_name != "-":
            self.__skill_info_prerequisite.configure(
                text=(skill.prereq_skill_name + " Lvl." +
                      str(skill.prereq_skill_lvl)))
        # If there is a prequisite skill.
        else:
            self.__skill_info_prerequisite.configure(text="None")

        self.__skill_info_points_to_up.configure(
            text=str(skill.points_to_up))

        if display_skill_level == "1":
            self.__skill_info_level_requirements.configure(
                text=skill.lvl_req[0])
        else:
            self.__skill_info_level_requirements.configure(
                text=skill.lvl_req[skill.skill_level-1])

        if skill.attack[0] == "-" or display_skill_level == "1":
            self.__skill_info_attack.configure(text=skill.attack[0])
        else:
            self.__skill_info_attack.configure(
                text=skill.attack[skill.skill_level - 1])

        # If nothing changes in the description with levels.
        if len(skill.description) == 1:
            self.__skill_info_description.configure(
                text=skill.description[0])
        # If some value changes in the description with levels.
        elif display_skill_level == "1":
            # 1 value changes
            if len(skill.description) == 6:
                self.__skill_info_description.configure(
                    text=skill.description[0].format(
                        skill.description[1]))
            # 2 values change
            if len(skill.description) == 11:
                self.__skill_info_description.configure(
                    text=skill.description[0].format(
                        skill.description[1], skill.description[6]))
        else:
            # 1 value changes
            if len(skill.description) == 6:
                self.__skill_info_description.configure(
                    text=skill.description[0].format(
                        skill.description[skill.skill_level]))
            # 2 values change
            if len(skill.description) == 11:
                self.__skill_info_description.configure(
                    text=skill.description[0].format(
                        skill.description[skill.skill_level],
                        skill.description[skill.skill_level + 5]))

    def update_skill_level_info(self, skill_string):
        """Updates the skills level indicator to match a change.
        :param skill_string: str, name of the skill.
        :return: NONE
        """
        (self.__skills_ui_elem_ALL[skill_string]["lvl_indicator"].
         configure(
            text=str(self.__skills[skill_string].skill_level)+"/5"))

    def deduct_skill_points(self, amount):
        """Deduct's skill points from the total and updates the
        "Available skill points" -indicator
        :param amount: int, amount to be reduced
        :return NONE
        """
        self.__skill_points -= amount
        self.__skill_points_indicator.configure(
            text="Available skill points: " + str(self.__skill_points))

    def skill_up_disable(self, skill_string):
        """Disables the skills level up button.
        :param skill_string: str, name of the skill.
        :return: NONE
        """
        self.__skills_ui_elem_ALL[skill_string]["up"]. \
            configure(bg="gray", state=DISABLED)

    def skill_up_enable(self, skill_string):
        """Enables the skills level up button.
        :param skill_string: str, name of the skill.
        :return: NONE
        """
        self.__skills_ui_elem_ALL[skill_string]["up"]. \
            configure(state=NORMAL, bg="green")

    def skill_down_disable(self, skill_string):
        """ s the skills level down button
        :param skill_string: str, name of the skill
        :return: NONE
        """
        self.__skills_ui_elem_ALL[skill_string]["down"]. \
            configure(state=DISABLED, bg="grey")

    def skill_down_enable(self, skill_string):
        """Enables the skills level down button
        :param skill_string: str, name of the skill
        :return: NONE
        """
        self.__skills_ui_elem_ALL[skill_string]["down"]. \
            configure(state=NORMAL, bg="red")

    def check_skill_requirements(self, skill_string):
        """Checks if the skills next levels requirements are met.
        Resets the skill and disables the skill up button if they arent,
        enables it if they are. Also disables skill up button if the
        skill is at its maximum level.
        :param skill_string: str, name of the skill
        :return: NONE
        """
        requirements_met = True
        # Shortened for easier usage, same practice in other functions
        # below.
        skill = self.__skills[skill_string]

        # Checks if skill is at it's maximum level or  at
        # the maximum level it can be at current character level
        if self.__char_lvl.get() == "" or skill.skill_level == skill.skill_max_level or skill.lvl_req[skill.skill_level] > int(self.__char_lvl.get()):
            requirements_met = False



        # If there is a prerequired skill, checks if it's level is high
        # enough.
        if skill.prereq_skill_name != "-":
            if self.__skills[skill.prereq_skill_name].\
                    skill_level < skill.prereq_skill_lvl:
                self.reset(skill_string)
                requirements_met = False

        if not requirements_met:
            self.skill_up_disable(skill_string)
        else:
            self.skill_up_enable(skill_string)

        # If very little skill points are left after upgrading,
        # requirements of all skills are tested to see if there's enough
        # left to upgrade them.
        if self.__skill_points < MOST_SKILL_POINTS_POSSIBLY_REQUIRED:
            self.check_if_enough_skill_points()

    def upgrade_skill(self, skill_string):
        """Upgrades the skill by one level and calls functions to
        update the UI.
        :param skill_string: str, name of the skill
        :return: NONE
        """
        skill = self.__skills[skill_string]
        skill.skill_level += 1

        # Downgrading enabled the first time a skill is upgraded.
        if skill.skill_level == 1:
            self.skill_down_enable(skill_string)

        # Updates the UI and skill point value
        self.update_skill_level_info(skill_string)
        self.deduct_skill_points(skill.points_to_up)
        self.update_skill_info_box(skill_string)

        # Checks other requirements.
        for skill_string2 in self.__skills:
            self.check_skill_requirements(skill_string2)

    def check_if_enough_skill_points(self):
        """Goes trough all skills and sees if there's enough skill
        points left to upgrade them. If not, skill up button is
        disabled.
        :return: NONE
        """
        for skill_string in self.__skills:
            if (self.__skills[skill_string].points_to_up >
                    self.__skill_points):
                self.skill_up_disable(skill_string)

    def downgrade_skill(self, skill_string):
        """ Downgrades the skill by one level and calls functions to
        update the UI.
        :param skill_string: str, name of the skill
        :return: NONE
        """
        skill = self.__skills[skill_string]
        skill.skill_level -= 1

        # Updates the UI and skill point value
        self.update_skill_level_info(skill_string)
        self.update_skill_info_box(skill_string)
        self.deduct_skill_points(-skill.points_to_up)

        # If the skill level is reduced down to 0, downgrade button is
        # disabled.
        if skill.skill_level == 0:
            self.skill_down_disable(skill_string)

        for skill_string2 in self.__skills:
            self.check_skill_requirements(skill_string2)

    def reset_all(self):
        """Resets all skills by calling the reset function one by one,
        and also checks their requirements after by calling the
        check_skill_requirements function.
        :return: NONE
        """
        for skill_string in self.__skills:
            self.reset(skill_string)
            self.check_skill_requirements(skill_string)

    def reset(self, skill_string):
        """Resets the skills level to 0 and updates its skill indicator.
        :param skill_string: str, name of the skill
        :return: NONE
        """
        # Skill points used on the skill are returned
        self.deduct_skill_points(
            (-self.__skills[skill_string].points_to_up *
             self.__skills[skill_string].skill_level))

        self.__skills[skill_string].skill_level = 0
        self.update_skill_level_info(skill_string)
        self.skill_up_enable(skill_string)
        self.skill_down_disable(skill_string)

    def change_level(self):
        """Change's the characters level. This also resets all made
        skill choices.
        :return: NONE
        """
        error = False

        try:
            char_lvl = int(self.__char_lvl.get())
        except ValueError:
            error = True

        if error or char_lvl <= 0:
            self.__skill_points_indicator.configure(
                text="Level must be a positive whole number")
            for skill_string in self.__skills:
                self.skill_up_disable(skill_string)
                self.skill_down_disable(skill_string)

        else:
            self.reset_all();
            self.__skill_points = 10 + 20 * (char_lvl - 1)
            self.__skill_points_indicator.configure(
                text="Available skillpoints: " + str(
                    self.__skill_points))
            for skill in self.__skills:
                self.check_skill_requirements(skill)


    def start(self):
        """ Starts the mainloop.
        :return: NONE
        """
        self.__window.mainloop()

    def stop(self):
        """Exits program
        :return: NONE
        """
        self.__window.destroy()


def main():

    skill_tree = SkillTree()
    skill_tree.start()


main()
