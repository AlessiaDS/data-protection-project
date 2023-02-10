import Table_Row


class Table:
    def __init__(self, noOfColumns, noOfRows):
        self.noOfColumns = noOfColumns
        self.noOfRows = noOfRows
        self.top_row = Table_Row()
        self.quasi_id = Table_Row()
        self.table_rows = list()
        self.table_columns = list()

        for _ in noOfRows:
            table_row = Table_Row()
            self.table_rows.append(table_row)

    def get_top_row(self):
        return self.top_row

    def get_quasi_id(self):
        return self.quasi_id

    def get_table_rows(self):
        return self.table_rows

    def set_top_row(self, data):
        self.top_row.add_data(data, 0)   # 0 to modify with our number of row


# /*set table values from file inputs*/
#      public void setTableValues(String fileLocation) throws FileNotFoundException{
#          File inputFile = new File(fileLocation);
#          //System.out.println("Exists: " + inputFile.exists());
#          //System.out.println("Can Read: " + inputFile.canRead());
#          Scanner infile = new Scanner(inputFile);
#          int x  = 1;//measure current row in table
#          while(infile.hasNextLine()){
#              String line  = infile.nextLine();
#              tableRows.add(new TableRow(line, x));
#              x++;
#          }
#      }

