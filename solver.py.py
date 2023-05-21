class solver():

    def __init__(self, generator):
        self.generator = generator
        self.domains = {
            var: self.generator.words.copy()
            for var in self.generator.vars
        }

    def word(self, assign):
        words = [
            [None for _ in range(self.generator.width)]
            for _ in range(self.generator.height)
        ]
        for var, word in assign.items():
            direction = var.direction
            for k in range(len(word)):
                i = var.i + (k if direction == var.DOWN else 0)
                j = var.j + (k if direction == var.ACROSS else 0)
                words[i][j] = word[k]
        return words


 

    def encourse(self):
        for var in self.domains:
            for val in self.domains[var].copy():
                if var.length != len(val):
                    self.domains[var].remove(val)    



    def rev(self, x, y):
        revd = False

        int = self.generator.overlaps[x, y]
        
        if int:
            i, j = int
        else:
            return False
            

        for x_word in self.domains[x].copy():
            error = all(x_word[i] != yt[j] for yt in self.domains[y])
            if error:
                self.domains[x].remove(x_word)
                revd = True

        return revd



    def assigning(self, assign):

        return all(bool(assign.get(var, None)) for var in self.domains)

    def ac(self, arcs=None):
        if arcs == None:
            arcs = [(x, y) for x in self.domains for y in self.domains if x!=y]


        while arcs != []:

            x, y = arcs.pop()

            if self.rev(x, y):
                if self.domains[x] == set():
                    return False
                for z in self.generator.same(x) - {y}:
                    arcs.append((z, x))

        return True


    def order(self, var, assign):
        last = {
            val: 0
            for val in self.domains[var]
        }

        sample = self.generator.same(var)

        for x_val in self.domains[var]:

            for similar in sample:
                
                if similar in assign:
                    continue

                i, j = self.generator.overlaps[var, similar]

                for y_val in self.domains[similar]:

                    if x_val[i] != y_val[j]:
                        last[x_val] += 1


        return sorted(last, key=last.get)




    def select_unassigned_var(self, assign):
        mvc = {}
        hdc = {}


        just_assign = True
        for var in self.domains:
            if var in assign:
                continue

            just_assign = False

            mvc[var] = len(self.domains[var])
            hdc[var] = len(self.generator.same(var))


        if just_assign:
            return None
        else:
            if min(mvc.values()) == max(mvc.values()):
                return max(hdc, key=hdc.get)
            else:
                return min(mvc, key=mvc.get)
  

    def Inference(self, assign, var):
        revult = {}

        domains_copy  = self.domains
        self.domains[var] = {assign[var]}

        same = self.generator.same(var)
        for similar in same:
            if similar in assign:
                continue
            kl = self.ac([(similar, var)])
            if not kl:
                self.domains = domains_copy
                return None


        for var in self.domains:
            if (var not in assign) and (len(self.domains[var]) == 1):
                revult[var] = next(iter(self.domains[var]))
        
        return revult



def main():

    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    generator = generator(structure, words)
    creator = generator(generator)
    assign = creator.solve()

    if assign is None:
        print("No solution.")
    else:
        crea.print(assign)
        if output:
            crea.save(assign, output)


if __name__ == "__main__":
    main()
