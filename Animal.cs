using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.UI;
public class Animal : Species
{
    //animal parameters
    [SerializeField]
    protected float reproductiveUrge = 0;
    protected float minHunger = 0;
    protected float maxHunger = 100;
    protected float minThirst = 0;
    protected float maxThirst = 100;
    [SerializeField]
    protected float hunger;             //starts at max
    [SerializeField]
    protected float thirst;             //start at max
    [SerializeField]
    protected float age;                // need to be initialised above zero so height and width can be calculated
    protected float deltaAge = 0;
    [SerializeField]
    protected float height = 0;
    [SerializeField]
    protected float width = 0;
    protected float deltaSize = 0;
    [SerializeField]
    protected float lifeSpan;
    protected GameObject carcass;
    [SerializeField]
    protected Gender gender;
    //movement
    [SerializeField]
    protected float movementSpeed=1.0f;
   
    //animal states
    [SerializeField]
    protected AnimalAction currentState;
    [SerializeField]
    protected HungerStates hungerState;


    protected Rigidbody2D rb2D;

    protected GameObject targetObject;
    protected GameObject closestWater;
    protected Node closestWaterNode;
    protected Node ClosestNodeNearWater;
    protected Node closestPlantNode;
    protected GameObject closestPlant;
    protected GameObject closestHerbivore;
    protected Node closestHerbivoreNode;
    protected GameObject closestCarnivore;
    protected Node closestCarnivoreNode;
    protected GameObject closestCarcass;
    protected Node closestCarcassNode;
    protected GameObject[] waters;
    protected List<Node> waterNodes=new List<Node>();

    protected GameObject[] plants;
    protected GameObject[] herbivores;
    protected GameObject[] carnivores;
    protected GameObject[] carcasses;
    protected Node currentNode;
    protected Node targetNode;
    protected bool findTarget=false;
    protected bool nextNode=true;
    protected bool moving = false;
    [SerializeField]
    protected bool left = false;
    
    protected List<Node> visited = new List<Node>();
    protected Node nextNodeToMoveTo;
    protected bool findWater = true;

    protected float birthYear;

    private void Start(){
        rb2D = GetComponent<Rigidbody2D>();
        //Physics2D.queriesStartInColliders = false; //insure Raycast does not detect object itself   
        birthYear=generateMap.getYears() + generateMap.getDays() / 360;
    }

    void Update()
    {

        //cap parmetres
        /*
        if (heading > 360)
            heading = 0;
        else if (heading < 0)
            heading = 360;
        if (hunger > maxHunger)
            hunger = 100;
        if (thirst > maxThirst)
            hunger = 100;
        */
        action();
        // Calls the function to increase the animals age.
        //increaseAge();

        //Debug.Log(currentState.ToString());


        animalParemeterUpdate();
        
        //removeWaterAmountTooSmall(waters);
        plants = GameObject.FindGameObjectsWithTag("Vegetation");
        herbivores = GameObject.FindGameObjectsWithTag("Herbivore");
        carnivores = GameObject.FindGameObjectsWithTag("Carnivore");
        carcasses = GameObject.FindGameObjectsWithTag("Carcass");

        
       // currentNode = new Node(new Vector2(10,10));
        //moveToNextNode();
    }
    private void FixedUpdate()
    {
        
        //vision();
        //moveUpdate();
        //moveAlongThePath();       
    }
    
    protected void finish(GameObject targetFood)
    {
        //float value = targetFood.GetComponent().getNutrionalValue();
        float value = 1;
        hunger += value * Time.deltaTime;

        Destroy(targetFood);
    }

    public void animalDeath()
    {
        Vector3 position = this.gameObject.transform.position;
        carcass = Instantiate(Resources.Load("Carcass", typeof(GameObject))) as GameObject;
        carcass.transform.position = new Vector3(position.x,position.y,position.z);
        carcass.transform.localScale = new Vector2(height, width);
        Carcass carcassTest = carcass.GetComponent<Carcass>();
        carcassTest.setConnectedNode(currentNode);
                

        //Debug.Log("Died to age");
    }

    public void animalDeathToCarnivore()
    {
        this.die();
        this.currentNode.setOccupied(false);
        this.nextNodeToMoveTo.setOccupied(false);
    }

    public void removeCurrent()
    {
        this.die();
        this.currentNode.setOccupied(false);
        this.nextNodeToMoveTo.setOccupied(false);
    }

    protected void animalParemeterUpdate()
    {
        float day = Time.fixedDeltaTime * 1.5f;
        //hungerstuff
        if (hunger != 0 || hunger != 100) { hunger -= (Time.deltaTime * 0.5f)*ParameterSettings.getHerbFoodRate();  }
        if (thirst != 0 || thirst != 100) { thirst -= (Time.deltaTime * 0.25f)*ParameterSettings.getHerbWaterRate(); }

        if (hunger <= minHunger){ animalDeath(); Debug.Log("Death to Hunger"); }
        if (thirst <= minThirst){ animalDeath(); Debug.Log("Death to Thirst"); }

        //Reproduction increases and decrease.
        //if()
        
        //thirst state change
        if (thirst < 50 && currentState != AnimalAction.DRINKING_WATER && currentState != AnimalAction.EATING)
        {
            moving = true;
            setCurrentState(AnimalAction.GOING_TO_WATER);
            if (findWater==true)
            {
                getClosestWater();
                findWater = false;
            }
            //if the target water node was occupied then find another water node;
            if (ClosestNodeNearWater.getOccupied() == true)
            {
                findWater = true;
                return;
            }


            }
        if (hunger < 50 && currentState != AnimalAction.EATING && currentState != AnimalAction.DRINKING_WATER)
        {
            moving = true;
            getClosestPlant();
            setCurrentState(AnimalAction.GOING_TO_FOOD);
            return;
        }

        if (hunger < 50 || thirst < 50 || currentState == AnimalAction.DRINKING_WATER || currentState == AnimalAction.EATING)
            return;

        if ((reproductiveUrge >= 100) && (hunger >= 50) && (thirst >= 50)&&(age>0.4f))
        {
            moving = true;
            setCurrentState(AnimalAction.SEARCH_FOR_MATE);
            getClosestHerbivoreMate();
            return;
        }
        if (thirst <= minThirst) { animalDeath(); Debug.Log("Death to Thirst"); }
        //reproductiveStuff
        //if (reproductiveUrge > 50) { currentState = AnimalAction.SEARCH_FOR_MATE; }
        if (reproductiveUrge <= 100) { reproductiveUrge += Time.deltaTime * 3 * ParameterSettings.getHerbReproRate(); }

        //base stateS
        if (hunger > 80 && reproductiveUrge < 80 && thirst>80) { currentState = AnimalAction.WANDERING; }
    }

    public void action()
    {
        if(currentState == AnimalAction.WANDERING)
        {
            wander();
        }
    }

    protected void moveToNextNode(Node nextNodeMove)
    {
        moving = true;
        //nextNodeToMoveTo = findNextNode();
        Vector3 direction = (nextNodeMove.getCentre() - new Vector2(transform.position.x, transform.position.y)).normalized;
        float dist = Vector2.Distance(nextNodeMove.getCentre(), transform.position);
        //rb2D.velocity = direction*new Vector2(2,2);
        rb2D.velocity = direction * movementSpeed;

        if (dist <= 1 || dist >= -1 && dist < 0)
        {
            //Debug.Log("distance" + dist);
            //transform.position = new Vector3(nextNodeMove.getCentre().x, nextNodeMove.getCentre().y, -5);
            generateMap.getNode(currentNode.getX(), currentNode.getY()).setOccupied(false);
            currentNode = nextNodeMove;

            if (nextNodeMove != targetNode)
            {
                Node node = findNextNode();
                //
                //generateMap.getNode(path[1].getX(), path[1].getY()).circleNode.GetComponent<Image>().color = new Color(1,0,0,1);
            }
            nextNode = true;
            moving = false;
        }

        if (currentNode == targetNode)
        {
            rb2D.velocity = new Vector2(0, 0);
        }
    }

    protected void moveAlongThePath()
    {
        //Debug.Log("target node = " + targetNode.getCentre());
        if (targetNode != null & currentNode != null)
        {
            if (!targetNode.getCentre().Equals(currentNode.getCentre()))
            {
                /*
                if(currentState == AnimalAction.GOING_TO_WATER)
                {
                    //getClosestWater();
                    targetNode = closestWaterNode;
                }
                */
                //Debug.Log("pulse = " + generateMap.getPulse());
                if (nextNode == true) // nextNode == true
                {
                    //Debug.Log("finds next Node");
                    nextNodeToMoveTo = findNextNode();
                    while (CompareNextNodes() == false)
                    {
                        nextNodeToMoveTo = findNextNode();
                    }
                    generateMap.getNode(nextNodeToMoveTo.getX(), nextNodeToMoveTo.getY()).setOccupied(true);
                    if (nextNodeToMoveTo.getX() > currentNode.getX())
                    {
                        left = false;
                    }
                    else
                    {
                        left = true;
                    }
                }
                else
                {
                    moveToNextNode(nextNodeToMoveTo);
                }
            }
            else if (visited.Count > 0)
            {
                resetVisited();
            }
        }
    }

    protected bool CompareNextNodes()
    {
        return true;
    }

    protected Node findNextNode()
    {       
        //Debug.Log("target node = " + targetNode.getCentre());
        Node node = Astar(currentNode, targetNode, visited);
        
        if((node.getCentre() == targetNode.getCentre()) && (generateMap.getNode(targetNode.getX(), targetNode.getY()).getOccupied()))
        {
            nextNode = true;
        }
        else
        {
            nextNode = false;
        }
        
        return node;
    }

    protected Node Astar(Node latestNode, Node target, List<Node> Visited)
    {
        float hValue;
        float smallestHValue = -1;
        int indexOfNextNode = 0;

        //Debug.Log("Read latestNode x and y:" + latestNode.getX()+","+ latestNode.getY()) ;
        Node[] adjacNodes = generateMap.getAdjacNodes(latestNode);


        for (int i = 0; i < adjacNodes.Length; i++)
        {
            if ((adjacNodes[i].getOccupied() == false) && adjacNodes[i].getX() != -1 && !isVisited(adjacNodes[i], Visited))//(adjacNodes[i].getOccupied() == false) && (!Visited.Contains(adjacNodes[i])) && 
            {

                //Debug.Log("adjacNodes[" + i + "] (" + adjacNodes[i].getX() + "," + adjacNodes[i].getY() + ")");
                hValue = evalH(adjacNodes[i], target);
                if (smallestHValue == -1)
                {

                    smallestHValue = hValue;
                    indexOfNextNode = i;

                }
                else if (hValue < smallestHValue)
                {

                    smallestHValue = hValue;
                    indexOfNextNode = i;

                }

            }
            else if ((target.getX() == adjacNodes[i].getX() && target.getY() == adjacNodes[i].getY()) && (adjacNodes[i].getOccupied() == false))
            {
                indexOfNextNode = i;

                //Debug.Log("adjacNodes[" + i + "]not looked at (" + adjacNodes[i].getX() + "," + adjacNodes[i].getY() + ")");
            }


        }
        if((target.getX() == adjacNodes[indexOfNextNode].getX() && target.getY() == adjacNodes[indexOfNextNode].getY()) && (adjacNodes[indexOfNextNode].getOccupied() == true))
        {
            return currentNode;
        }
        //Debug.Log("return from A*"+ adjacNodes[indexOfNextNode].getX()+","+ adjacNodes[indexOfNextNode].getY());

        return adjacNodes[indexOfNextNode];        
  
        /*
         * 1.find adaj closest towards target
         * 2.Add to path
         * 3.  = 1,2
        */
    }

    //calculate the H value
    protected float evalH(Node nodeA, Node nodeB)
    {
        int distX = Mathf.Abs(nodeA.getX() - nodeB.getX());
        int distY = Mathf.Abs(nodeA.getY() - nodeB.getY());

        
        
        return distX+distY; 
    }


    //check if the node in the path
    private bool isVisited(Node n, List<Node> nList)
    {
        foreach (Node temp in nList)
        {
            if (temp.getX() == n.getX() && temp.getY() == n.getY())
                return true;
        }
            return false;
    }

    public void wander()
    {
        //targetNode = generateMap.nodes[6,6];
        if (targetNode is null) {
            generateWanderNode();
        }
        else
        {
            generateWanderNode();
        }
       
    }

    private void generateWanderNode()
    {
        Node[] availableNodes = generateMap.getAdjacNodes(currentNode);
        int randInt = (int)Random.Range(0, 7.9f);
        //Debug.Log("Index = " + randInt);
        if ((availableNodes[randInt].getX() != -1) && (availableNodes[randInt].getOccupied() == false))//(adjacNodes[i].getOccupied() == false) && (!Visited.Contains(adjacNodes[i])) && 
        {
            //Debug.Log("adjacNodes[" + i + "] (" + adjacNodes[i].getX() + "," + adjacNodes[i].getY() + ")");
            targetNode = availableNodes[randInt];
        }
    }

    //public IEnumerator wander()
    //{  
    //    int LorR          = Random.Range(0, 2);
    //    int walkTime      = Random.Range(1, 4);
    //    int walkWait      = Random.Range(1, 4);
    //    int rotationTime  = Random.Range(1, 3);
    //    int rotationWait  = Random.Range(1, 4);
    //
    //    currentState = AnimalAction.WANDERING;
    //
    //    yield return new WaitForSeconds(walkWait);
    //    isMoving = true;
    //    yield return new WaitForSeconds(walkTime);
    //
    //    isMoving = false;
    //    yield return new WaitForSeconds(rotationWait);
    //    if (LorR == 1)
    //    {
    //        rb2D.velocity = new Vector2(0.0f, 0.0f); //stops it from moving while turning
    //        isRotatingRight = true;
    //        yield return new WaitForSeconds(rotationTime);
    //        isRotatingRight = false;
    //    }
    //    else if (LorR == 2)
    //    {
    //        rb2D.velocity = new Vector2(0.0f, 0.0f); //stops it from moving while turning
    //        isRotatingLeft = true;
    //        yield return new WaitForSeconds(rotationTime);
    //        isRotatingLeft = false;
    //    }
    //    currentState = AnimalAction.NONE;
    //}

    //utility stuff
    public void setCurrentState(AnimalAction state){ currentState = state; }
    
    protected void addHunger(float value){ hunger += value; }
    

    protected void goToObject(GameObject targetObeject)
    {

        Vector3 direction = (targetObeject.transform.position - transform.position).normalized;
        //transform.Translate(direction * Time.deltaTime * movementSpeed);
        //rb2D.MovePosition(rb2D.transform.position + direction * movementSpeed);
        rb2D.velocity = direction * movementSpeed; //  stops it from jittering slowly towards the water.
        //Debug.Log("moved");
    }

    protected void drinkingWater()
    {      
                  
        while (thirst < 90) {
            moving = false;
            rb2D.velocity = new Vector2(0, 0);
            thirst += Time.deltaTime * 3;
            if (thirst >= 90)
            {
                currentState = AnimalAction.WANDERING;
            }
        }
        
    }

    protected void eatingFood()
    {
        float timer = 0.5f;
        if (timer>0)
        {
            rb2D.velocity = new Vector2(0, 0);
            hunger += Time.deltaTime * 3;
            timer -= Time.deltaTime;
            if(hunger>70)
                currentState = AnimalAction.NONE;
            
        }
        if (hunger >= 90)
        {
            currentState = AnimalAction.NONE;
        }
    }
    
    /*
    protected void reporducing()
    {
        Debug.Log("Reproducing");
        List<Node> birthNodes = new List<Node>(); // list of possible birth nodes

        foreach (Node n in generateMap.getAdjacNodes(closestHerbivoreNode))
        {
            if (n.getX() != -1 && !n.getOccupied())
                birthNodes.Add(n);
        }


        if (gameObject.GetComponent<HerbivoreAction>().GetGender().Equals(Gender.FEMALE))
        {
            if (!birthNodes.Any()) {
                reproductiveUrge = 80;
                Debug.Log("Birth failed no possible location to give birth");
                currentState = AnimalAction.WANDERING;
                return;
            }
            int index = Random.Range(0, birthNodes.Count);
            Node randomBirth = birthNodes[index];
            GameObject newHerb;
            newHerb = (GameObject)Resources.Load("herbivoreTest", typeof(GameObject)); //Load prefab
            newHerb = Instantiate(newHerb, new Vector3(randomBirth.getCentre().x, randomBirth.getCentre().y, -5), Quaternion.identity);
            HerbivoreAction herb = newHerb.GetComponent<HerbivoreAction>();

            herb.setNode(randomBirth);
            herb.setGender(Random.Range(0, 2));
            generateMap.getNode(randomBirth.getX(), randomBirth.getY()).setOccupied(true);
            //randomBirth.setOccupied(true);
            Debug.Log("Gave birth");
            herb.setCurrentState(AnimalAction.WANDERING);

        }

        reproductiveUrge = 0;
        currentState = AnimalAction.WANDERING;

    }
    */
    //find the node around the water 
    protected void getClosestWater()
    {
        waters = GameObject.FindGameObjectsWithTag("WaterSprite");
        //find closest water obj
        float closestDist = generateMap.getMapDiagonal();
        if(waters != null)
        foreach (GameObject water in waters)
        {
            waterNodes.AddRange(water.GetComponent<WaterSpite>().getWaterSpriteNodes());
            float dist = Vector2.Distance(water.transform.position, transform.position);
            if (dist < closestDist)
            {
                closestWater = water;
                closestDist = dist;
            }
        }

        //find closest water node
        closestDist = generateMap.getMapDiagonal();
        if (waterNodes != null)
        {
            foreach (Node water in closestWater.GetComponent<WaterSpite>().getWaterSpriteNodes())
            {
                Debug.Log("finding closest water node");
                float dist = Vector2.Distance(water.getCentre(), transform.position);
                if (dist < closestDist)
                {
                    closestWaterNode = water;
                    closestDist = dist;
                }
                
            }
        }

        //find the nearest node outside the water
        closestDist = generateMap.getMapDiagonal();
        List<Node> nodesAroundWater = new List<Node>();

        foreach (Node n in generateMap.getAdjacNodes(closestWaterNode))
        {   
            //if the node near water is the currentNode, jump out the function
            if(n.getCentre()==currentNode.getCentre())
            {
                ClosestNodeNearWater = n;
                return;
            }

            if (n.getX() != -1 && !n.getOccupied()) // Finds available
                nodesAroundWater.Add(n);
        }
        
        if (nodesAroundWater != null)
        {
            foreach (Node n in nodesAroundWater)
            {
                if (!n.getOccupied())
                {
                    float dist = Vector2.Distance(n.getCentre(), transform.position);
                    if (dist < closestDist)
                    {
                        ClosestNodeNearWater = n;
                        closestDist = dist;
                    }
                }
                
                

            }

        }

        /*
        if ((closestWaterNode != null) && (nodeNearWater != null))
        {
            Debug.Log("Water found at "+ nodeNearWater.getX()+","+ nodeNearWater.getY());
        }
        else
        {
            Debug.Log("Water not found");
        }
        */
    }

    protected void getClosestPlant() 
    {
        float closestDist = 10000;
        foreach (GameObject plant in plants) 
        {
            if (plant != null) //I CHANGED THIS TO PLANT FROM CLOSEST PLANT. idk if thats what u wanted but it works now so idk.
            {
                float dist = Vector3.Distance(plant.transform.position, transform.position);
                if (dist < closestDist)
                {
                    closestPlant = plant;
                    closestDist = dist;
                }
            }
        }
        closestPlantNode = closestPlant.GetComponent<Vegetation>().nodeConnectedTo;
    }
    /*
    protected void getClosestPlantNode()
    {
        Node node = currentNode;
        float closestDistance = 10000;
        foreach(Node n in generateMap.nodes)
        {
            float dist = Vector3.Distance(closestPlant.transform.position, new Vector3(n.getCentre().x, n.getCentre().y, -5));
            if(dist < closestDistance)
            {
                closestDistance = dist;
                node = n;
            }
        }
        closestPlantNode = node;
    }
    */

    protected void getClosestHerbivore() 
    {
        herbivores = GameObject.FindGameObjectsWithTag("Herbivore");
        float closestDist = 25;

        foreach (GameObject herbivore in herbivores)
        {
            float dist = Vector3.Distance(herbivore.transform.position, transform.position);
            if (dist < closestDist)
            {
                closestHerbivore = herbivore;
                closestDist = dist;
            }
        }

        if (closestHerbivore != null)
        { 
            closestHerbivoreNode = closestHerbivore.GetComponent<HerbivoreAction>().getCurrentNode();
        }
       
    }

    protected void getClosestHerbivoreMate()
    {
        herbivores = GameObject.FindGameObjectsWithTag("Herbivore");
        Gender mateGaneder= Gender.MALE;

        closestHerbivore = null;
        if(gender.Equals(Gender.MALE))
        {
            mateGaneder = Gender.FEMALE;
        }

        float closestDist = 10000;
        herbivores = GameObject.FindGameObjectsWithTag("Herbivore");
        //get herbiovre with correct gender
        foreach (GameObject herbivore in herbivores)
        {
            if (herbivore.GetComponent<HerbivoreAction>().GetGender().Equals(mateGaneder) && (herbivore.GetComponent<HerbivoreAction>().getAge() >= 0.4f) &&
                herbivore.GetComponent<HerbivoreAction>().getRUrge() >= 100f)
            {
                float dist = Vector3.Distance(herbivore.transform.position, transform.position);
                if (dist < closestDist)
                {
                    closestHerbivore = herbivore;
                    closestDist = dist;
                }
            }
        }

        if (closestHerbivore is null)
        {
            Debug.Log("No mates found");
            wander();
        }

        if (closestHerbivore != null) {
            closestHerbivoreNode = closestHerbivore.GetComponent<HerbivoreAction>().getCurrentNode();
        }

    }

    //protected void getClosestCarcass()
    //{
    //    carcasses = GameObject.FindGameObjectsWithTag("Carcass");

    //    float closestDist = 10000;
    //    foreach (GameObject carcass in carcasses)
    //    {
    //        float dist = Vector3.Distance(carcass.transform.position, transform.position);
    //        if (dist < closestDist)
    //        {
    //            closestCarcass = carcass;
    //            closestDist = dist;
    //        }
    //    }
    //}
    protected void getClosestCarcass()
    {
        float closestDist = 25;
        carcasses = GameObject.FindGameObjectsWithTag("Carcass");
        foreach (GameObject carcass in carcasses)
        {
            if (carcass != null)
            {
                float dist = Vector3.Distance(carcass.transform.position, transform.position);
                if (dist < closestDist)
                {
                    closestCarcass = carcass;
                    closestDist = dist;
                    closestCarcassNode = closestCarcass.GetComponent<Carcass>().getConnectedNode();
                }
            }
        }
    }

    protected void getClosestCarnivore()
    {
        float closestDist = 10000;
        carnivores = GameObject.FindGameObjectsWithTag("Carnivore");
        
        Gender mateGaneder = Gender.MALE;
        if (gender.Equals(Gender.MALE))
        {
            mateGaneder = Gender.FEMALE;
        }
       
        foreach (GameObject carnivore in carnivores)
        { 
            //get carnivore with correct gender
            if (carnivore.GetComponent<CarnivoreAction>().GetGender().Equals(mateGaneder))
            {
                float dist = Vector3.Distance(carnivore.transform.position, transform.position);
                if (dist < closestDist)
                {
                    closestCarnivore = carnivore;
                    closestDist = dist;
                }
            }
        }
        if (closestCarnivore != null)
        {
            closestCarnivoreNode = closestCarnivore.GetComponent<CarnivoreAction>().getCurrentNode();
        }

    }

    public void IncOrDecAge(bool increase)
    {
        if(increase)
        {
            deltaAge = deltaAge + 0.5f;
        }
        else
        {
            deltaAge = deltaAge - 0.5f;
        }
    }

    public void IncOrDecLifeSpan(bool increase)
    {
        if (increase)
        {
            lifeSpan = lifeSpan + 0.2f;
        }
        else
        {
            lifeSpan = lifeSpan - 0.2f;
        }
    }

    public void IncOrDecHunger(bool increase)
    {
        if (increase)
        {
            hunger = hunger + 5f;
        }
        else
        {
            hunger = hunger - 5f;
        }
    }

    public void IncOrDecThirst(bool increase)
    {
        if (increase)
        {
            thirst = thirst + 5;
        }
        else
        {
            thirst = thirst - 5;
        }
    }

    public void IncOrDecSize(bool increase)
    {
        if (increase)
        {
            deltaSize = deltaSize + 0.05f;
        }
        else
        {
            deltaSize = deltaSize - 0.05f;
        }
    }

    public void IncOrDecReproUrge(bool increase)
    {
        if (increase)
        {
            reproductiveUrge = reproductiveUrge + 5;
        }
        else
        {
            reproductiveUrge = reproductiveUrge - 5;
        }
    }

    public float getAge()
    {
        return age;
    }

    public float getLifeSpan()
    {
        return lifeSpan;
    }

    public float getHunger()
    {
        return hunger;
    }

    public float getThirst()
    {
        return thirst;
    }

    public float getHeight()
    {
        return height;
    }

    public float getWidth()
    {
        return width;
    }

    public float getRUrge()
    {
        return reproductiveUrge;
    }

    public AnimalAction getState()
    {
        return currentState;
    }

    public Gender GetGender()
    {
        return gender;
    }

    public void setGender(int i)
    {
        if(System.Enum.IsDefined(typeof(Gender), i))
        {
            gender = (Gender)i;
        }
        else
        {
            Debug.Log("Gender number not valid");
        }
    }

    public void setNode(Node node)
    {
        currentNode = node;
    }

    public void resetVisited()
    {
        visited.Clear();
    }
    public Node getCurrentNode()
    {
        return currentNode;
    }

    //void vision()
    //{
    //    Vector2 startPosition = (Vector2)transform.position + new Vector2(0.5f, 0.2f);
    //    RaycastHit2D hit = Physics2D.Raycast(transform.position, vectorFromHeading(heading), animalViewDistance);
    //    Debug.DrawRay(transform.position, vectorFromHeading(heading) * animalViewDistance, Color.white);
    //    if (hit == false) { //Debug.Log("okay?");
    //    }

    //    else if (hit.collider.tag.Equals("grassFood"))
    //    {
    //        //Debug.Log("Hitting: " + hit.collider.tag);
    //    }
    //    else if (!hit.collider.tag.Equals("grassFood"))
    //    {
    //        //Debug.Log("other");
    //    }
    //}

    /*The animal will first move to the target node and when it reaches the node, it will move towards the target object*/
    protected void moveToStatic(Node nodeToMove, GameObject targetObject)
    {

        if (currentNode.getX() == targetNode.getX() && currentNode.getY() == targetNode.getY())
        {
            goToObject(targetObject);
            return;
        }

        if (!(nodeToMove is null))
        {
            targetNode = nodeToMove;
            //findNextNode();
            //moveAlongThePath();
        }
        else
        {
            Debug.Log(" not find target node");
            currentState = AnimalAction.WANDERING;
        }

        

    }

    protected void moveToDynamic(Node nodeToMove, GameObject target)
    {
        targetNode = nodeToMove;
        targetObject = target;
        Physics2D.IgnoreCollision(this.GetComponent<Collider2D>(), target.GetComponent<Collider2D>(), false);
        if (Vector2.Distance(targetNode.getCentre(), currentNode.getCentre()) < Mathf.Sqrt(2) * 5.12f)
            goToObject(targetObject);
        else
        {
            findNextNode();
            moveAlongThePath();
        }

    }
}




