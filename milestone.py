def sf2github(sfMilestone):
    state = "closed" if sfMilestone["complete"] else "open"

    return {
        'title' : sfMilestone["name"],
        'state' : state,
        'description' : sfMilestone["description"],
        'due_on' : sfMilestone["due_date"]
    }
