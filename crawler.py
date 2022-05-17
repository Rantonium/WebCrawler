import requests
from bs4 import BeautifulSoup

master_page_url = "https://samples.vx-underground.org/samples/Families/"


def get_master_page_soup():
    master_page = requests.get(master_page_url)
    master_page_soup = BeautifulSoup(master_page.content, "html.parser")
    return master_page_soup


def get_child_page_soup(child_page_name):
    child_page = requests.get('%s%s/' % (master_page_url, child_page_name))
    child_page_soup = BeautifulSoup(child_page.content, "html.parser")
    return child_page_soup


def get_child_info_from_list(children):
    children_info = []

    for child in children[2:]:
        columns = child.find_all('td')
        child_link, child_size, child_date = columns[0].text, columns[1].text, columns[2].text
        children_info.append([child_link, child_size, child_date])

    return children_info


def get_children_info(name):
    child_page_soup = get_child_page_soup(name)

    if "Samples" in child_page_soup.text:
        next_child_page_soup = get_child_page_soup(name + "/Samples")
        children = next_child_page_soup.find_all("tr")
    else:
        children = child_page_soup.find_all("tr")

    children_info = get_child_info_from_list(children)

    return children_info


safety_counter = 0
max_requests = 3
if __name__ == "__main__":
    families = dict()

    master_soup = get_master_page_soup()
    links = master_soup.find_all("td", class_="link")

    for link in links[1:]:
        families[link.text] = []
        if safety_counter < max_requests:
            families[link.text] = get_children_info(link.text)
            safety_counter += 1

    for family_name in families.keys():
        print(family_name)
        print(families[family_name])
