import matplotlib
import matplotlib.pyplot as plt

def make_fig(filename, title, y, colors):
    """
    Arguments: str filename, str title, str y, lst colors

    Returns: NONE

    Creates a figure using data from filename titled title with an
    x axis of gender and a y axis of y, with colors for the color of each bar.
    """
    labels = ["Male", "Female", "Other"]
    data = []

    with open(filename) as f:
        lines = f.readlines()
        for i in range(1, len(lines)):
            data.append(int(lines[i].split(",")[-1].strip()))
                 
    plt.figure(figsize=(20,10)) 
    container = plt.bar(labels, data, color = colors)
    plt.bar_label(container)
    plt.title(title, size = 24)
    plt.xlabel("Gender", size = 14, labelpad = 10)
    plt.ylabel(y, size = 14, labelpad = 10)

    png_name = title.replace(" ", "_")
    plt.savefig(f"{png_name}.png")
    plt.show()


def main():
    colors = ["cornflowerblue", "hotpink", "orange"]
    make_fig("gender_by_comics.csv", "Heroes by Gender in Marvel Comics", "Number of Issues", colors)
    make_fig("most_played_characters.csv", "Heroes by Gender in Marvel Rival Matches", 
             "Number of Matches Played In", colors)


if __name__ == "__main__":
    main()