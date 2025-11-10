from libcst_analysis_tools.analyze_complete import get_all_classes_with_methods_from_file
import inspect 
from textual.app import App


RANDOM_CELEBRITIES = ["Ada Lovelace", "Alan Turing", "Grace Hopper", "Linus Torvalds", "Margaret Hamilton", "Tim Berners-Lee", "Katherine Johnson", "Dennis Ritchie", "Barbara Liskov", "James Gosling"] 
RANDOM_COUNTRIES   = ["USA", "UK", "Canada", "Germany", "France", "Japan", "Australia", "India", "Brazil", "Italy"]
def tabular_data(rows_count)->list[tuple]:
    list_ = []
    # Header
    list_.append(("ID", "Name", "Country", "Time (s)"))
    for i in range(rows_count):
        celebrity=RANDOM_CELEBRITIES[i % len(RANDOM_CELEBRITIES)]
        country  =RANDOM_COUNTRIES[i % len(RANDOM_COUNTRIES)]
        time=50.0 + i*0.1
        list_.append( (i, celebrity, country, time) )
    return list_

def tree_data():
    return get_all_classes_with_methods_from_file(inspect.getfile(App))
def tree_title():
    # just get the 2 last parts of the path
    return f"Classes and Methods in {'/'.join(inspect.getfile(App).split('/')[-2:])}"