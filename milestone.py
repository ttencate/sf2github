from datetime import datetime

def sf2github(sfMilestone):
    state = "closed" if sfMilestone["complete"] else "open"
    ghMilestone = {
        'title' : sfMilestone["name"],
        'state' : state,
    }

    if sfMilestone["description"] != "":
        ghMilestone["description"] = sfMilestone["description"]

    if sfMilestone["due_date"] != "":
        sfDate = datetime.strptime(sfMilestone["due_date"], "%m/%d/%Y")
        ghMilestone['due_on'] = sfDate.strftime("%Y-%m-%d") + "T00:00:00Z"

    return ghMilestone
