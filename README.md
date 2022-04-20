# Project description
+Research Problem+: Multi-player game framework to minimize unemployment and poverty while intervening on minimum wage and interest rates.
+Methods+: Model-Based Reinforcement Learning and Adversarial Training
+Data+: Synthetic Data from a built-in parameterized economics simulation data generative model
+Master Thesis: Akshay Gudi
+Advisors HPI+: Prof. Holger Giese, Christian Adriano 
+Advisors SAP: Frank Feinbube

# Endpoints - Web based simulator

**base_url = http://ccloud@minwage-app.sp.only.sap:8000**

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
    * Endpoint: base_url/start-game
    * Authorization: API Key  Token <>

4. Perform Action (In front of "Token" add API Token acquired from "/api-token-auth" endpoint)
    (Add value of minimum wage in place of <action-value> )
    * Method : GET
    * Endpoint: base_url/perform-action/<action-value>
    * Authorization: API Key  Token <>
  
5. End Game (In front of "Token" add API Token acquired from "/api-token-auth" endpoint)
    * Method : GET
    * Endpoint: base_url/end-game
    * Authorization: API Key  Token <>
