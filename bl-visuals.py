import matplotlib
import matplotlib.pyplot as plt

def make_fig(filenames, title, subname1, subname2, colors):
    """
    Arguments: filenames, title subname1, subname2, colors

    Returns: None

    Creating a figure of two barcharts, names of files from list (filenames) to get data,
    title will be the title of the figure, subname1 and subname2 are for chart names,
    colors will be a list of the colors used to distinguish (Male, Female, Other) on both graphs
    """
    labels = ["Male", "Female", "Other"]
    comic_data = []
    with open(filenames[0]) as file:
        lines = file.readlines()
        for line in range(1,4): #skipping headers
            data = int(lines[line].split(",")[-1])
            comic_data.append(data)

    game_data = []
    with open(filenames[1]) as file:
        lines = file.readlines()
        for line in range(1,4):
            data = int(lines[line].split(",")[-1])
            game_data.append(data)
    
    fig, (ax1, ax2) = plt.subplots(1,2, figsize = (20,10))

    fig.suptitle(title, y = .97, size = 30)
    ax1.set_title(subname1, size = 18, pad = 10)
    container = ax1.bar(labels,comic_data,color=colors)
    ax1.bar_label(container)
    ax1.set_xlabel("Gender", size = 14, labelpad = 10)
    ax1.set_ylabel("Number of Issues", size = 14, labelpad = 10)
    ax2.set_title(subname2, size = 18, pad = 10)
    container = ax2.bar(labels,game_data,color=colors)
    ax2.bar_label(container)
    ax2.set_xlabel("Gender", size = 14, labelpad = 10)
    ax2.set_ylabel("Number of Matches Played In", size = 14, labelpad = 10)

    fig.savefig(f"{title}.png")

    plt.show()

def main():
    data = ["gender_by_comics.csv", "most_played_characters.csv"]
    title = "Heroes by Gender in Marvel Comics and Marvel Rivals"
    colors = ["cornflowerblue", "hotpink", "orange"]
    make_fig(data, title, "Heroes by Gender in Marvel Comics", "Heroes by Gender in Marvel Rival Matches", colors)


if __name__ == "__main__":
    main()