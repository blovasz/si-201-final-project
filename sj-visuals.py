import matplotlib.pyplot as plt
import re

def piechart(filename):
    """
    Arg: str filename
    Out: none
    """
    numbers = []
    labels = []
    with open(filename, "r") as file:
        for line in file:
            numbers.append(re.findall(r"\d+", line)[0])
            labels.append((re.findall(r"from (.+)", line)[0], int(re.findall(r"\d+", line)[0])))
    plt.figure(figsize=(10, 8))
    plt.pie(
        numbers,
        labels=labels,
        startangle=90,
        colors=plt.cm.Paired.colors
    )
    plt.title("Superhero Count by Place of Birth")
    plt.tight_layout()
    plt.show()

def barchart(filename):
    """
    Arg: str filename
    Out: none
    """
    labels = []
    numbers = []
    with open(filename, "r") as file:
        for line in file:
            numbers.append(float(re.findall(r"\d+\.\d+", line)[0]))
            labels.append(re.findall(r"for (\w+)", line)[0])
    plt.figure(figsize=(8, 6))
    plt.bar(labels, numbers, color="skyblue", edgecolor="black")
    for i in range(len(numbers)):
        val = numbers[i]
        plt.text(i, val + 0.5, f"{val:.2f}", ha="center", va="bottom")
    plt.title("Average BMI of Superheroes by Gender")
    plt.ylabel("BMI")
    plt.tight_layout()
    plt.show()

def main():
    """
    Arg: none
    Out: none
    """
    piechart("num_superhero_by_origin.txt")
    barchart("average_bmi_by_gender.txt")

if __name__ == "__main__":
    main()