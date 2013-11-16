def sf2github(sfTickets):
    return {
        'title' : sfTickets["summary"],
        'body' : sfTickets["description"],
    }
