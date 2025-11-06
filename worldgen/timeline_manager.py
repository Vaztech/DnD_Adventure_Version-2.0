def log_events(events):
    timeline = {}
    for event in events:
        year = event["year"]
        if year not in timeline:
            timeline[year] = []
        timeline[year].append(event["description"])
    return timeline
