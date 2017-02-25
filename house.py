class House(object):
    address = ""
    cost_per_week = 0
    url = ""
    distance_to_work = 9999999
    distance_to_school = 9999999

    # The class "constructor" - It's actually an initializer
    def __init__(self, address, cost_per_week, url):
        self.address = address
        self.cost_per_week = cost_per_week
        self.url = url


def create_house(address, cost_per_week, url):
    house = House(address, cost_per_week, url)
    return house