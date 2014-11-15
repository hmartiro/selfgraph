"""

"""


if __name__ == '__main__':

    import sys, yaml
    in_file = sys.argv[1]

    with open(in_file) as file:
        data_str = file.read()
        print(data_str)
        data = yaml.load(data_str)

    #print(data)
