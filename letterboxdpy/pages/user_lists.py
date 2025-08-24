from letterboxdpy.utils.lists_extractor import ListsExtractor
from letterboxdpy.constants.project import DOMAIN


class UserLists:

    def __init__(self, username: str) -> None:
        self.username = username
        self.url = f"{DOMAIN}/{self.username}/lists"
        
    def get_lists(self) -> dict: 
        return ListsExtractor.from_url(self.url)

if __name__ == "__main__":
    lists_instance = UserLists("fastfingertips")

    for id, data in lists_instance.get_lists()['lists'].items():
        for key, value in data.items():
            print(f"{key}: {value}")
        print("-"*100)