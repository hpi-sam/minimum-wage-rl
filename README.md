# Project description
+Research Problem+: Multi-player game framework to minimize unemployment and poverty while intervening on minimum wage and interest rates.
+Methods+: Model-Based Reinforcement Learning and Adversarial Training
+Data+: Synthetic Data from a built-in parameterized economics simulation data generative model
+Master Thesis: Akshay Gudi
+Advisors HPI+: Prof. Holger Giese, Christian Adriano 
+Advisors SAP: Frank Feinbube

# Endpoints - Web based simulator
**base_url = http://ccloud@minwage-app.sp.only.sap:8080**

1. Create User
    * Method: POST
    * Endpoint: base_url/reg-user
    * Input:
      ```javascript
      {"username":"My-User-Name",
      "password":"My-Password",
      "email":"myemail@email.com"}
      ```
    
2. Getting API Token
    * Method : POST
    * Endpoint : base_url/api-token-auth
    * Input:
      ```javascript
      {"username":"My-User-Name", "password":"My-Password"}
      ```
    * Response:
      ```javascript
      {"token": "<token here>",
      "user_id": "<id here>",
      "email": "<email here>"}
      ```

3. Start Game 
    * Method : GET
    * Endpoint: base_url/start-game?level=<level_number>
    * Authorization: API Key  Token <>
    * Response:
      ```javascript
      {"status": 200,
      "message": {
         "User Data": {
            "Year": 1,
            "Unemployment Rate": 100,
            "Poverty Rate": 100,
            "Minimum wage": 7,
            "Inflation Rate": 0,
            "population": 1500
                },
          "AI Data": {
            "Year": 1,
            "Unemployment Rate": 100,
            "Poverty Rate": 100,
            "Minimum wage": 7,
            "Inflation Rate": 0,
            "population": 1500
                },
          "end flag": false,
          "message": ""
            }
         }
      ```

4. Perform Action
    * Method : POST
    * Endpoint: base_url/perform-action/<action-value>
    * Authorization: API Key  Token <>
    * Input: ```javascript {"minimum_wage": <value>}```
    * Response (For last step of game):
      ```javascript
      {
        "status": 200,
        "message": {
          "User Data": {
               "Year": 30,
               "Minimum wage": 7.1,
               "Unemployment Rate": 0,
               "Poverty Rate": 46.86,
               "Quantity": 1395,
               "Inflation": -0.01,
               "Product Price": 7.32,
               "Population": 1848,
               "Small Companies": 0,
               "Medium Companies": 0,
               "Large Companies": 6,
               "Bank Balance": 656117.4013145872,
               "Retired Current Year": 0,
               "Start Up Founders Current Year": 0
          },
         "AI Data": {
               "Year": 30,
               "Minimum wage": 10.74,
               "Unemployment Rate": 0,
               "Poverty Rate": 2.98,
               "Quantity": 29925,
               "Inflation": 0.98,
               "Product Price": 11.96,
               "Population": 1848,
               "Small Companies": 0,
               "Medium Companies": 0,
               "Large Companies": 6,
               "Bank Balance": 323638.6078008192,
               "Retired Current Year": 0,
               "Start Up Founders Current Year": 0
                },
          "game_stats": {
               "player_game_stats": {
                     "year": 30,
                     "average_poverty": 69.76,
                     "average_unemployment": 16.13,
                     "average_inflation": 0.22,
                     "average_product_price": 11.41,
                     "average_minimum_wage": 7.1
                     },
               "ai_game_stats": {
                    "year": 30,
                    "average_poverty": 32.84,
                    "average_unemployment": 18.71,
                    "average_inflation": 0.4,
                    "average_product_price": 11.87,
                    "average_minimum_wage": 9.39
                     }
                },
          "interact": {
               "emotion": "",
               "comments": [
                  { "role": 1, "Message": "" },
                  {"role": 3, "Message": ""}],
               "has_comments": false
                   },
          "end flag": true,
          "message": {"message": "End of Episode"}
        }
      }
      ```
  
5. Stop Game: To stop the game before last step of episode
    * Method : GET
    * Endpoint: base_url/stop-game
    * Authorization: API Key  Token <>
    * Response
      ```javascript
      {
       "status": 200,
       "message": {
           "player_game_stats": {
               "year": 11,
               "average_poverty": 93.74,
               "average_unemployment": 50.32,
               "average_inflation": 0.69,
               "average_product_price": 19.17,
               "average_minimum_wage": 7.56
                 },
           "ai_game_stats": {
               "year": 11,
               "average_poverty": 70.92,
               "average_unemployment": 50.4,
               "average_inflation": 0.7,
               "average_product_price": 16.53,
               "average_minimum_wage": 8.32
                 }
             }
      }
      ```

6. Save and End Game: Option to save the game
    * Method : GET
    * Endpoint: base_url/save-game?save_game=false
    * Authorization: API Key  Token <>

# Launch the Application using Docker
   
   1. Switch to the branch 'new-web-branch'.
         `git checkout new-web-branch`
   2. Launch Docker container
         `docker compose build`
         `docker compose up`
   4. Access the application using above end-points at address `localhost:8080/` using Postman.
   5. Stop the containers after using the application
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
