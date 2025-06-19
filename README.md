# ChessRl
![image](https://github.com/user-attachments/assets/ca8efbc9-83b7-4a26-a38f-3c0abe391343)

ChessRl is the self-play Agent which learns to play chess through reinforcement learning


## Technologies

- Python 3.12
- PyTorch
- Gymnasium
- React v19 (nvm v24.0.2)


## Agent Models

* 4GB VRAM GPU
    ```
    chess_model = ChessPolicy(
        conv_layers_num=3,
        in_channels_list=[12, 64, 128],
        out_channels_list=[64, 128, 256],
        kernel_size_list=[3, 3, 3],
        fc_layers_num=2,
        fc_in_features_list=[16384, 2048],
        fc_out_features_list=[2048, ACTION_SPACE],
    ).to(device=device)
    ```


## Getting Started (Linux)

### Agent Training (Self Play)

##### General config: backend/config.py 
##### Agent config: backend/chess_agent/agent_config.py

* Install packages 
    ```
    pip install -r requirments.txt
    ```
  
* Modify .env
    ```
    SAVED_MODELS_PATH="/path/to/saved_models"
    SAVED_GAMES_PATH="/path/to/saved_games"
    SAVED_GRAPHS_PATH="/path/to/graphs"
    ```

* To train the model run backend/main.py.
* After training, model will be saved in the backend/saved_models
* You can also load a previously saved model to continue training (check INIT_EPISODE and EPISODES)


### Backend

* Change and run scripts/run-api-local.sh
    ```
    #!/bin/bash

    cd /path/to/chess-rl/ || exit
    uvicorn backend.api.main:app --reload
    ```

### Frontend

* Install nvm v24.0.2
    ```
    nvm install v24.0.2
    nvm use v24.0.2
    ```
  
* Modify chess-rl-frontend/.env.development
    ```
    REACT_APP_ENV=development
    PORT=3007
    REACT_APP_API_URL=http://localhost:8000
    ```

* Install packages
    ```
    npm install
    ```

* Run frontend
    ```
    npm start
    ```

* Enjoy!

![image](https://github.com/user-attachments/assets/0e8e8404-56a0-42f4-8134-47a2937d03c6)

