def  ufc(final, initial):
     
    global Graph,COST
    solution = []

    queue = []# creating a queue1riority queue
 
    for i in range(len(final)):
        solution.append(10**8)
 
    queue.append([0, initial])
 
    visit = {}
    count = 0
 
    while (len(queue) > 0):
 
        queue = sorted(queue)
        queue1 = queue[-1]
 
        del queue[-1]
 
        queue1[0] *= -1
 
        if (queue1[1] in final):
            index = final.index(queue1[1])
 
            if (solution[index] == 10**8):
                count += 1
 
            if (solution[index] > queue1[0]):
                solution[index] = queue1[0]
 
            del queue[-1]
 
            queue = sorted(queue)
            if (count == len(final)):
                return solution
 
        if (queue1[1] not in visit):
            for i in range(len(Graph[queue1[1]])):
 
                queue.append( [(queue1[0] + COST[(queue1[1], Graph[queue1[1]][i])])* -1, Graph[queue1[1]][i]])
 
        visit[queue1[1]] = 1
 
    return solution
 
# main function
if __name__ == '__main__':
     
    # create the Graph
    Graph,COST = [[] for i in range(8)],{}
 
    # add edge
    Graph[0].append(1)
    Graph[0].append(3)
    Graph[3].append(1)
    Graph[1].append(6)
    Graph[4].append(2)
    Graph[4].append(5)
    Graph[2].append(1)
    Graph[5].append(2)
    Graph[5].append(6)
    Graph[6].append(4)
 
    #COSTs from state to state
    COST[(0, 1)] = 2
    COST[(0, 3)] = 5
    COST[(1, 6)] = 1
    COST[(3, 1)] = 5
    COST[(3, 6)] = 6
    COST[(3, 4)] = 2
    COST[(2, 1)] = 4
    COST[(4, 2)] = 4
    COST[(4, 5)] = 3
    COST[(5, 2)] = 6
    COST[(5, 6)] = 3
    COST[(6, 4)] = 7
 
    #Final state
    final = []

    final.append(3)#3 is considered as final state 
 
    solution = ufc(final, 0)
 
    print("Minimum COST from 0 to 3 is = ",solution[0])
