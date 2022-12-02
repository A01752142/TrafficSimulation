from mesa import Agent

# Clase de Auto
class Car(Agent):
    """
    Car
    Attributes:
        unique_id: Agent's ID
        direction:
        read the direction on the road
    """
    def __init__(self, unique_id, pos, model):
        """
        Creates a new car
        Args:
            unique_id: The agent's ID
            pos: the agents position
            model: Model reference for the agent
        """
        super().__init__(unique_id, model)
        self.id = unique_id
        self.model = model
        self.pos = pos
        self.direccion = None

    # funcion de movimiento
    def move(self, pos):
        """
        moves the car on the road
        """
        self.model.grid.move_agent(self, pos)
        
    # funcion de paso
    def step(self):
        """
        Determines the new direction it will take, and then moves
        """
        # print("soy el coche" + str(self.id))
        # print("estoy en " + str(self.pos))

        # Leer Ubicacion actual
        this_cell = self.model.grid.get_cell_list_contents([self.pos])
        (x, y) = self.pos

        # Si se encuentra sobre una calle lee en que direccion va
        calle = [obj for obj in this_cell if isinstance(obj, Road)]
        if len(calle) != 0:
            calle = calle[0]
            # dependiendo de ella se ve posicion siguiente
            if calle.direction == "Left":
                x -= 1
                self.direccion = "Left"
            elif calle.direction == "Right":
                x += 1
                self.direccion = "Right"
            elif calle.direction == "Up":
                y += 1
                self.direccion = "Up"
            elif calle.direction == "Down":
                y -= 1
                self.direccion = "Down"

            # se checa que no exceda los limites del mapa
            if x < self.model.width and y < self.model.height:
                siguiente_posicion = (x, y)
            else:
                siguiente_posicion = self.pos
            
            # se checa que la posible celda siguiente este vacia y no tenga semaforos
            contenidos = self.model.grid.get_cell_list_contents([siguiente_posicion])
            auto = [obj for obj in contenidos if isinstance(obj, Car)]

            semaforo = [obj for obj in contenidos if isinstance(obj, Traffic_Light)]
            if len(semaforo) == 0:
                if len(auto) == 0:
                    self.move(siguiente_posicion)
                else:
                    # si si esta ocupada la celda siguiente, el auto busca rebasar
                    vecinos = self.model.grid.get_neighborhood(
                                self.pos,
                                moore=False,
                                include_center=False)

                    for posicion in vecinos:
                        contenidos = self.model.grid.get_cell_list_contents([posicion])
                        
                        coches = [obj for obj in contenidos if isinstance(obj, Car)]
                        calles = [obj for obj in contenidos if isinstance(obj, Road)]
                        # checar si hay autos
                        # si no los hay, se mueve lateralmente
                        if len(calles) > 0 and len(coches) == 0:
                            self.move(posicion)

            else:
                # en caso de que hubiera semaforo, se ve su color
                semaforo = semaforo[0]
                #print('Hay un semaforo!')
                # si esta en verde sigue
                if semaforo.color == True:
                    self.move(siguiente_posicion)
                #else:
                    #print("el semaforo esta en rojo, no me puedo mover")
        
        # en caso de que se encuentra directamente sobre un semaforo
        # se sigue la direccion que tenia en el turno anterior
        semaforo = [obj for obj in this_cell if isinstance(obj, Traffic_Light)]
        if len(semaforo) != 0:
            if self.direccion == "Left":
                self.move((x-1, y))
            if self.direccion == "Right":
                self.move((x+1, y))
            if self.direccion == "Up":
                self.move((x, y+1))
            if self.direccion == "Down":
                self.move((x, y-1))


# Clase de Semaforo
class Traffic_Light(Agent):
    """
    Traffic Light agent. Tells Cars When They Can Cross And When They Cant
    """
    def __init__(self, unique_id, model, color=False, timeToChange=10):
        super().__init__(unique_id, model)
        self.color = color
        self.timeToChange = timeToChange

    def step(self):
        # modificarlo para que en vez de ser fijo, dependa de si hay coches vecinos o no, 
        # que se coordinen entre los de la misma interseccion para que solo uno este prendido a la vez
        if self.model.schedule.steps % self.timeToChange == 0:
            self.color = not self.color
        # pass


# Clase de Destino
class Destination(Agent):
    """
    Destination agent. Spawns and absorbs Cars.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.recien_creo = False
        self.model = model
        self.id = unique_id

    def step(self):
        # obten estado de calles vecinas
        vecinos = self.model.grid.get_neighborhood(
            self.pos,
            moore=False,  # Boolean for whether to use
                          # Moore neighborhood (including diagonals) or
                          # Von Neumann (only up/down/left/right).
            include_center=False)

        #print('vecinos:' + str(vecinos))

        for posicion in vecinos:
            contenidos = self.model.grid.get_cell_list_contents([posicion])
            # checar si hay autos
            coches = [obj for obj in contenidos if isinstance(obj, Car)]
            calles = [obj for obj in contenidos if isinstance(obj, Road)]
            flip = self.random.choice([0, 0, 0, 0, 1])
            #if len(coches) > 0:
                # si hay un coche:
                # si 0 / 1 -> quita o no ese coche
            #    if not flip:
            #        print('un auto ha llegado a su destino en ' + str(posicion))
            #        car = self.random.choice(coches)
            #        self.model.grid.remove_agent(car)
            #        self.model.schedule.remove(car)
            #elif len(calles) > 0:
                # si estan vacias:
                # si 0 / 1 -> pones o no pones coche
            #    if flip:
            #        print('un auto se ha incorporado al trafico en' + str(posicion))
            #       car = Car(self.model.next_id(), posicion, self.model)
            #        self.model.grid.place_agent(car, posicion)
            #        self.model.schedule.add(car)
            #        self.recien_creo = True

# Clase de Obstaculo
class Obstacle(Agent):
    """
    Obstacle agent. Just to add obstacles to the grid.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass

# Clase de Calle
class Road(Agent):
    """
    Road agent. Tells Cars Where they Should Move Next.
    """
    def __init__(self, unique_id, model, direction="Left"):
        super().__init__(unique_id, model)
        self.direction = direction
        self.model = model

    def step(self):
        pass
