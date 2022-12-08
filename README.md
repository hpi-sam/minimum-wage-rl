# Project description
+Research Problem+: Multi-player game framework to minimize unemployment and poverty while intervening on minimum wage and interest rates.
+Methods+: Model-Based Reinforcement Learning and Adversarial Training
+Data+: Synthetic Data from a built-in parameterized economics simulation data generative model
+Master Thesis: Akshay Gudi
+Advisors HPI+: Prof. Holger Giese, Christian Adriano 
+Advisors SAP: Frank Feinbube

# Endpoints - Web based simulator


Old version **base_url = http://ccloud@minwage-app.sp.only.sap:8000**

or

New version **base_url = http://ccloud@minwage-app.sp.only.sap:8001**


Latest version **base_url = http://ccloud@minwage-app.sp.only.sap:8002**

1. Create User
    * Method: POST
    * Endpoint: base_url/reg-user
    * Input: ```{ "username":"My-User-Name", "password":"My-Password", "email":"myemail@email.com" }```
    
2. Getting API Token
    * Method : POST
    * Endpoint : base_url/api-token-auth
    * Input: ```{ "username":"My-User-Name", "password":"My-Password" }```

3. Start Game (In front of "Token" add API Token acquired from "/api-token-auth" endpoint)
    * Method : GET
    * Endpoint: base_url/start-game?level=<level_number>
    * Authorization: API Key  Token <>

4. Perform Get Action (In front of "Token" add API Token acquired from "/api-token-auth" endpoint)
    * Method : GET
    * Endpoint: base_url/perform-get-action?minimum_wage=<value for minimum wage>
    * Authorization: API Key  Token <>

5. Perform Action (In front of "Token" add API Token acquired from "/api-token-auth" endpoint)
    * Method : POST
    * Endpoint: base_url/perform-action/<action-value>
    * Authorization: API Key  Token <>
    * Input: ```{ "minimum_wage": <value> }```
  
6. End Game (In front of "Token" add API Token acquired from "/api-token-auth" endpoint)
    * Method : GET
    * Endpoint: base_url/end-game
    * Authorization: API Key  Token <>

# Launch the Application using Docker
   
   1. Switch to the branch 'web-branch'.
         `git checkout web-branch`
   2. Launch Docker container
         `docker compose up`
   3. Access the application using above end-points at address `localhost:8080/` using Postman.
   4. Stop the containers after using the application
         `docker compose down`

# Hints to play
   
   1. **If you see Bank balance is moderate but, product price is high.**
      * Increase minimum wage by little bit or decrease it a bit.
      * This causes low inflation or negative inflation and makes country to import products rather than increasing the price.
  
   2. **If bank balance is low and product price moderate, but people poor because of low minimum wage.**
      * Then increase minimum wage more than hint 1.
      * This causes minimum wage to increase however product prices will also increase.
   
   3. **If bank balance is high, product price is high, people are poor.**
      * Then you can increase minimum wage even more (more than hint-2), this causes country to import lot of products instead of increasing product price. 
      * However bank balance will decrease considerably while importing, that is why lot of bank-balance is needed.
