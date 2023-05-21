import sys

from crossword import *



class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assign):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assign.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assign):
        """
        Print crossword assign to the terminal.
        """
        letters = self.letter_grid(assign)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assign, filename):
        """
        Save crossword assign to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assign)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        
        # loop through each variable domain and remove values of unequal length
        for var in self.domains:
            for val in self.domains[var].copy():
                if var.length != len(val):
                    self.domains[var].remove(val)




    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        
        revised = False

        # if two variables don't overlap with each other, return False
        intersects = self.crossword.overlaps[x, y]
        
        if intersects:
            i, j = intersects
        else:
            return False
            

        # remove the values from x that has no corresponding values in y
        for x_word in self.domains[x].copy():
            query = all(x_word[i] != y_word[j] for y_word in self.domains[y])
            if query:
                self.domains[x].remove(x_word)
                revised = True

        return revised




    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """

        # list all the arcs if arc is not given
        if arcs == None:
            arcs = [(x, y) for x in self.domains for y in self.domains if x!=y]


        # loop until the arcs is empty
        while arcs != []:

            x, y = arcs.pop()

            if self.revise(x, y):
                if self.domains[x] == set():
                    return False
                for z in self.crossword.neighbors(x) - {y}:
                    arcs.append((z, x))

        return True




    def assign_complete(self, assign):
        """
        Return True if `assign` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        
        return all(bool(assign.get(var, None)) for var in self.domains)



    def consistent(self, assign):
        """
        Return True if `assign` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        # keep track of all variable combinations 
        var_list = []

        # loop over all variables in assign
        for x in assign:
            for y in assign:

                var_list.append((x, y))

                # if the variables are same or it has already been executed, continue 
                if (x == y) or ((y, x) in var_list):
                    continue

                # calculate if x and y overlaps but have different letters in intersection, return false
                intersects = self.crossword.overlaps[x, y]
                if intersects:
                    i, j = intersects
                    if assign[x][i] != assign[y][j]:
                        return False

                # remove  the duplicates from the assign
                if assign[x] == assign[y]:
                    return False

        return True




    def order_domain_values(self, var, assign):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        # create a dictionary where each key is variable and their value is number of values ruled out in
        # their neighbors
        least_constraints = {
            val: 0
            for val in self.domains[var]
        }

        neighbors_list = self.crossword.neighbors(var)

        # loop over all values and neighbors of the given variable
        for x_val in self.domains[var]:

            for neighbor in neighbors_list:
                
                if neighbor in assign:
                    continue

                i, j = self.crossword.overlaps[var, neighbor]

                # loop over each values of the neighbor
                for y_val in self.domains[neighbor]:

                    # if the intersection do not match, the values in neighbor is ruled out
                    if x_val[i] != y_val[j]:
                        least_constraints[x_val] += 1


        return sorted(least_constraints, key=least_constraints.get)




    def select_unassigned_variable(self, assign):
        """
        Return an unassigned variable not already part of `assign`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        
        # make a dictionary for minimum value constraint and highest degree constraint
        mvc = {}
        hdc = {}


        # looop over each variable domain and update the mvc and hdc dictionary
        no_unassigned_var = True
        for var in self.domains:
            if var in assign:
                continue

            no_unassigned_var = False

            mvc[var] = len(self.domains[var])
            hdc[var] = len(self.crossword.neighbors(var))


        # if all variables have same values remaining, choose the value with highest degree
        if no_unassigned_var:
            return None
        else:
            if min(mvc.values()) == max(mvc.values()):
                return max(hdc, key=hdc.get)
            else:
                return min(mvc, key=mvc.get)


    def Inference(self, assign, var):
        """
        for  each variable assigned in an assign, runs ac3 function to enforce arc
        consistency in every neighbors and updates self.domain 

        """

        result = {}

        # update the domain for assigned variable
        domains_copy  = self.domains
        self.domains[var] = {assign[var]}

        # enforce node consistency to the neighbors of given variable
        neighbors = self.crossword.neighbors(var)
        for neighbor in neighbors:
            if neighbor in assign:
                continue
            arc_consistent = self.ac3([(neighbor, var)])
            if not arc_consistent:
                self.domains = domains_copy
                return None


        # return the variables with only one remaining values
        for var in self.domains:
            if (var not in assign) and (len(self.domains[var]) == 1):
                result[var] = next(iter(self.domains[var]))
        
        return result



    def backtrack(self, assign):
        """
        Using Backtracking Search, take as input a partial assign for the
        crossword and return a complete assign if possible to do so.

        `assign` is a mapping from variables (keys) to words (values).

        If no assign is possible, return None.
        """

        # if all the assigns are made, return assign
        if self.assign_complete(assign):
            return assign

        # if a variable is node consistent, put it in assign
        for var in self.domains:
            if (len(self.domains[var]) ==  1) and  (var not in assign):
                assign[var] = next(iter(self.domains[var]))


        # select unassigned variable 
        var = self.select_unassigned_variable(assign)
        if var is None:
            return None

        # loop  over all values in that variable
        for val in self.order_domain_values(var, assign):

            # assign a variable to a value
            new_assign = assign.copy()
            new_assign[var] = val

            #create a copy of domain if inference fails
            domains_copy = self.domains.copy()

            inference = self.Inference(new_assign, var)
            if inference is not None:
                new_assign.update(inference)
            else:
                continue
            
            # check the consistency of new_assign
            if self.consistent(new_assign):
                result = self.backtrack(new_assign)

                if result is not None:
                    return result

        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assign = creator.solve()

    # Print result
    if assign is None:
        print("No solution.")
    else:
        creator.print(assign)
        if output:
            creator.save(assign, output)


if __name__ == "__main__":
    main()
