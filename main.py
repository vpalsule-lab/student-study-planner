set_website_title("Student Study Planner")
set_site_information(
    author="Vineet Palsule",
    description="Allows college students to organize and plan their assignments.",
    sources="Thanks to the Drafter docs and LLM.",
    planning=["CS1 Final Project 0_ Pick a Problem (1).pdf", "CS1 Final Project 1_ Design.pdf"],
    links=["https://github.com/vpalsule-lab/student-study-planner"]
)
hide_debug_information()
set_website_framed(False)



from drafter import *
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from bakery import assert_equal


# Different course options

COURSE_OPTIONS = [
    "Computer Science",
    "Chemistry",
    "English",
    "Math",
    "Biology",
    "Other"
]


# Assignment and State dataclasses

@dataclass
class Assignment:
    """
    This dataclass stores the information for one school assignment.
    It takes the name, course, due date, estimated time to complete, and if the assignment
    is completed or not.
    """
    name: str
    course: str
    due_date: str
    estimated_hours: float
    completed: bool


@dataclass
class State:
    """
    This dataclass stores information that must be available across the website.
    """
    assignments: list[Assignment]
    student_name: str
    selected_course: str
    total_completed: int
    status_message: str


# Helper functions

def assignment_description(assignment: Assignment) -> str:
    """
    This function returns the assignment description.
    It gives the completed status if the assignment is completed
    and returns the assignment with its details and its completion status.
    """
    if assignment.completed:
        status = "Completed"
    else:
        status = "Not completed"

    return (
        assignment.name + " | " + assignment.course
        + " | Due: " + assignment.due_date
        + " | Estimated hours: " + str(assignment.estimated_hours)
        + " | " + status
    )


def valid_date(date_text: str) -> bool:
    """
    This function checks that a date is written in the MM-DD-YYYY format.
    It returns false if it isn't in the right format.
    """
    try:
        datetime.strptime(date_text, "%m-%d-%Y").date()
        return True
    except ValueError:
        return False


def is_upcoming(assignment: Assignment) -> bool:
    """
    This funciton returs true for unfinished assignments due in the next 7 days.
    It takes the timedelta function and if it is within 7 days of the due date,
    it will go into the website as upcoming.
    """
    today = date.today()
    last_day = today + timedelta(days=7)

    if assignment.completed:
        return False

    if not valid_date(assignment.due_date):
        return False

    due = datetime.strptime(assignment.due_date, "%m-%d-%Y").date()
    return today <= due <= last_day


def is_overdue(assignment: Assignment) -> bool:
    """
    This function returs true for unfinished assignments with a past due date.
    If the assignment is not completed and the current date is past the due date,
    then it will go into the website as overdue.
    """
    if assignment.completed:
        return False

    if not valid_date(assignment.due_date):
        return False

    due = datetime.strptime(assignment.due_date, "%m-%d-%Y").date()
    return due < date.today()


def remaining_hours(state: State) -> float:
    """
    This function adds the estimated hours for all unfinished assignments.
    It starts with a total of 0.0 hours and adds the estimated hours to complete
    to the total variable and returns the total remaining time needed
    for all the unfinished assignments.
    """
    total = 0.0

    for assignment in state.assignments:
        if not assignment.completed:
            total += assignment.estimated_hours

    return total



# Home Page route

@route
def index(state: State) -> Page:
    """
    This route shows the homepage and links to the planner pages.
    """
    content = [
        Header("Student Study Planner"),
        "Welcome, " + state.student_name + "!",
        "Keep your college assignments and deadlines organized.",
        Header("Your Progress"),
        "Total assignments: " + str(len(state.assignments)),
        "Completed assignments: " + str(state.total_completed),
        "Estimated hours remaining: " + str(remaining_hours(state)),
        Header("Navigation"),
        Button("Add an Assignment", "add_assignment_page"),
        Button("View All Assignments", "view_assignments"),
        Button("Upcoming and Overdue Work", "upcoming_deadlines"),
        Button("Completed Assignments", "completed_assignments"),
        Button("Filter by Course", "filter_assignments"),
        Header("Change Your Name"),
        TextBox("new_name", state.student_name),
        Button("Save Name", "save_student_name"),
        state.status_message
    ]
    return Page(state, content)


# Save student name route

@route
def save_student_name(state: State, new_name: str) -> Page:
    """
    This route updates the student's name.
    It takes the input from the state.student_name and updates the name.
    """
    if new_name.strip() != "":
        state.student_name = new_name.strip()
        state.status_message = "Your name was updated."
    else:
        state.status_message = "Please enter a name."

    return index(state)



# Add assignment page route

@route
def add_assignment_page(state: State) -> Page:
    """
    This route shows the form used to enter a new assignment.
    It contains all the information for the assignment, such as
    name, course, due date, and estimated time to complete.
    """
    content = [
        Header("Add an Assignment"),
        "Assignment name:",
        TextBox("assignment_name"),
        "Course:",
        SelectBox("course", COURSE_OPTIONS),
        "Due date (MM-DD-YYYY):",
        TextBox("due_date"),
        "Estimated hours to complete:",
        TextBox("estimated_hours", "1.0"),
        Button("Add Assignment", "submit_assignment"),
        Button("Back to Home", "index"),
        state.status_message
    ]
    return Page(state, content)


# Submit assignment route

@route
def submit_assignment(
    state: State,
    assignment_name: str,
    course: str,
    due_date: str,
    estimated_hours: str
) -> Page:
    """
    This route checks if the assignment information is correct.
    If everything is correct, then it will add the assignment to the list.
    """
    if assignment_name.strip() == "":
        state.status_message = "Enter an assignment name."
    elif course not in COURSE_OPTIONS:
        state.status_message = "Choose a course from the list."
    elif not valid_date(due_date):
        state.status_message = "Enter the date as MM-DD-YYYY."
    else:
        try:
            hours = float(estimated_hours)

            if hours <= 0:
                state.status_message = "Estimated hours must be above zero."
            else:
                new_assignment = Assignment(
                    assignment_name.strip(),
                    course,
                    due_date,
                    hours,
                    False
                )
                state.assignments.append(new_assignment)
                state.status_message = "Assignment added successfully."
        except ValueError:
            state.status_message = "Enter a valid number of hours."

    return add_assignment_page(state)



# View all assignments route

@route
def view_assignments(state: State) -> Page:
    """
    This route shows every assignment and completion buttons for unfinished work.
    The student can see all the assignments can allows them to see what is completed
    or incomplete.
    """
    content = [Header("All Assignments")]

    if len(state.assignments) == 0:
        content.append("You have not added any assignments yet.")
    else:
        for index, assignment in enumerate(state.assignments):
            content.append(assignment_description(assignment))

            if not assignment.completed:
                content.append(
                    Button(
                        "Mark as Completed",
                        "complete_assignment",
                        [Argument("assignment_index", index)]
                    )
                )

    content.extend([
        Header("Work Summary"),
        "Completed: " + str(state.total_completed),
        "Estimated hours remaining: " + str(remaining_hours(state)),
        Button("Add an Assignment", "add_assignment_page"),
        Button("Back to Home", "index")
    ])
    return Page(state, content)




# Mark assignment as completed route

@route
def complete_assignment(state: State, assignment_index: int) -> Page:
    """
    This route finds the assignment by marking the selected assignment
    and marks it as finished. It will update the count of
    completed assignments.
    """
    if 0 <= assignment_index < len(state.assignments):
        assignment = state.assignments[assignment_index]

        if not assignment.completed:
            assignment.completed = True
            state.total_completed += 1
            state.status_message = (
                assignment.name + " was marked completed."
            )
        else:
            state.status_message = "That assignment is already completed."
    else:
        state.status_message = "The selected assignment was not found."

    return view_assignments(state)




# Upcoming and overdue assignments route

@route
def upcoming_deadlines(state: State) -> Page:
    """
    This route shows unfinished assignments that are due soon
    and assignments that are past the due date.
    """
    content = [
        Header("Upcoming Deadlines"),
        "Unfinished assignments due within the next 7 days:"
    ]
    found_upcoming = False

    for assignment in state.assignments:
        if is_upcoming(assignment):
            content.append(assignment_description(assignment))
            found_upcoming = True

    if not found_upcoming:
        content.append("There are no upcoming deadlines.")

    content.append(Header("Overdue Assignments"))
    found_overdue = False

    for assignment in state.assignments:
        if is_overdue(assignment):
            content.append(assignment_description(assignment))
            found_overdue = True

    if not found_overdue:
        content.append("There are no overdue assignments.")

    content.extend([
        Button("View All Assignments", "view_assignments"),
        Button("Back to Home", "index")
    ])
    return Page(state, content)




# Course filter page route

@route
def filter_assignments(state: State) -> Page:
    """
    This route shows a select box so a student can select the
    course they want.
    """
    content = [
        Header("Filter Assignments by Course"),
        "Choose a course to view:",
        SelectBox(
            "course_choice",
            ["All Courses"] + COURSE_OPTIONS,
            state.selected_course
        ),
        Button("Show Assignments", "choose_course"),
        Button("Back to Home", "index")
    ]
    return Page(state, content)




# Save the selected course route

@route
def choose_course(state: State, course_choice: str) -> Page:
    """
    This route saves the selected course the student picked
    and show its assignments.
    """
    valid_choices = ["All Courses"] + COURSE_OPTIONS

    if course_choice in valid_choices:
        state.selected_course = course_choice
        state.status_message = "Showing " + course_choice + " assignments."
    else:
        state.status_message = "Please choose a valid course."

    return filtered_assignments(state)




# Display filtered assignments route

@route
def filtered_assignments(state: State) -> Page:
    """
    This route displays assignments only from the selected course.
    """
    content = [
        Header("Filtered Assignments"),
        "Selected course: " + state.selected_course
    ]
    found_assignment = False

    for index, assignment in enumerate(state.assignments):
        if (
            state.selected_course == "All Courses"
            or assignment.course == state.selected_course
        ):
            content.append(assignment_description(assignment))
            found_assignment = True

            if not assignment.completed:
                content.append(
                    Button(
                        "Mark as Completed",
                        "complete_assignment",
                        [Argument("assignment_index", index)]
                    )
                )

    if not found_assignment:
        content.append("No assignments match this course.")

    content.extend([
        Button("Choose Another Course", "filter_assignments"),
        Button("Back to Home", "index")
    ])
    return Page(state, content)




# Completed assignments route

@route
def completed_assignments(state: State) -> Page:
    """
    This route shows all the assignments that
    the student has finished.
    """
    content = [Header("Completed Assignments")]
    found_assignment = False

    for assignment in state.assignments:
        if assignment.completed:
            content.append(assignment_description(assignment))
            found_assignment = True

    if not found_assignment:
        content.append("You have not completed any assignments yet.")

    content.extend([
        "Total completed: " + str(state.total_completed),
        Button("View All Assignments", "view_assignments"),
        Button("Back to Home", "index")
    ])
    return Page(state, content)


# Sample unit tests

sample_assignment = Assignment(
    "Chemistry Homework",
    "Chemistry",
    "12-01-2026",
    2.0,
    False
)

sample_state = State(
    [sample_assignment],
    "Student",
    "All Courses",
    0,
    ""
)

assert_equal(
    assignment_description(sample_assignment),
    "Chemistry Homework | Chemistry | Due: 12-01-2026"
    " | Estimated hours: 2.0 | Not completed"
)

assert_equal(remaining_hours(sample_state), 2.0)
assert_equal(valid_date("12-01-2026"), True)
assert_equal(valid_date("not-a-date"), False)


# Test that the homepage route returns a page with the same state.
assert_equal(index(sample_state).state.student_name, "Student")


# Test the name route.
save_student_name(sample_state, "Alex")
assert_equal(sample_state.student_name, "Alex")


# Test the add_assignment page.
assert_equal(
    add_assignment_page(sample_state).state.assignments,
    [sample_assignment]
)


# Test adding an assignment with its information.
submit_assignment(
    sample_state,
    "Math Homework",
    "Math",
    "12-05-2026",
    "3"
)
assert_equal(len(sample_state.assignments), 2)


# Test viewing assignments.
assert_equal(
    view_assignments(sample_state).state.assignments,
    sample_state.assignments
)


# Test completing an assignment.
complete_assignment(sample_state, 0)
assert_equal(sample_state.assignments[0].completed, True)
assert_equal(sample_state.total_completed, 1)


# Test the deadline, filter, and completed-assignment routes.
assert_equal(
    upcoming_deadlines(sample_state).state.assignments,
    sample_state.assignments
)
assert_equal(
    filter_assignments(sample_state).state.selected_course,
    "All Courses"
)

choose_course(sample_state, "Chemistry")
assert_equal(sample_state.selected_course, "Chemistry")

assert_equal(
    filtered_assignments(sample_state).state.selected_course,
    "Chemistry"
)
assert_equal(
    completed_assignments(sample_state).state.total_completed,
    1
)



# Website information and startup

set_site_information(
    "YOUR NAME",
    "A study planner that helps college students organize assignments "
    "and manage deadlines.",
    "Created using Python and the Drafter library.",
    "See the project planning document in the GitHub repository.",
    []
)

set_website_title("Student Study Planner")


# Starting the website server

start_server(
    State(
        [],
        "Student",
        "All Courses",
        0,
        "Welcome to your Study Planner!"
    )
)

