from datetime import datetime

def sf2github(sfMilestone):
    state = "closed" if sfMilestone["complete"] else "open"

    ghDate = ""
    if sfMilestone["due_date"] != "":
        sfDate = datetime.strptime(sfMilestone["due_date"], "%m/%d/%Y")
        ghDate = sfDate.strftime("%Y-%m-%d") + "T00:00:00Z"

    return {
        'title' : sfMilestone["name"],
        'state' : state,
        'description' : sfMilestone["description"],
        'due_on' : ghDate
    }
