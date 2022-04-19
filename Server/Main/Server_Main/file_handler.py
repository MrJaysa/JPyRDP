from json import (
    load as json_loader,
    dump as json_dumper
)

class Details_Handler():
    # details is a list of dicts
    def __init__(self):
        self.path = "Main/Observed/sock.json"

    def new_connection(self, name):
        with open(self.path) as file:
            data = json_loader(file)
        data[name] += 1
        self.save(data)

    def rem_connection(self, name):
        with open(self.path) as file:
            data = json_loader(file)
        data[name] -= 1
        self.save(data)
        
    def save(self, data):
        with open(self.path, "w") as file:
            json_dumper(data, file, indent=4)


