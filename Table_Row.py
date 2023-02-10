class Table_row:
    def __init__(self):
        self.noOfRows = 0
        self.data = list()

    def add_data(self, noOfRows, data):
        self.noOfRows = noOfRows
        stringArray = data.split(",")
        for i in stringArray:
            self.data.append(i)

    def get_data(self):
        return self.data

    def check_equality(self, row):
        if self.data.len() != row.data.len():
            return 0
        else:
            for d in self.data:
                if self.data.index(d) != row.data.index(d):
                    return 0
        return 1

    def table_copy(self):
        new_table_row = Table_row()
        new_table_row.noOfRows = self.noOfRows
        for i in self.data:
            new_table_row.data.append(self.data.index(i))
            return new_table_row

    def row_print(self):
        for i in self.data.len():
            print(self.data.index(i))
