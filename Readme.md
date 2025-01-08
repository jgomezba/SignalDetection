# Signal detection with intersection points

This project leverages Machine Learning techniques to geolocate signals from unknown emitters, based on the collection of intersection points of received signals. The goal is to accurately predict the location of emitters using data from multiple receiving stations and their corresponding measurements.

![image](https://github.com/user-attachments/assets/bad4a472-3f41-4fcc-9c23-6063f9c055ed)

## How to use this repository

1. Install requirements txt using command `python -m pip install -r requirements.txt` ![image](https://github.com/user-attachments/assets/a7293152-c062-4eca-bd75-54951838866b)

2. Execute script `models.py` and change parameters to see adjustment ![image](https://github.com/user-attachments/assets/ddf191e3-ec08-401f-bdd1-21c7126b4ac5) ![image](https://github.com/user-attachments/assets/cab7db04-5c36-46d0-ab36-e6a213db53b2)


## Notes

Data used in models is available in folder `Sample_Data\For_Modeling`:
1. datosMarcacionesES_1733999425626_1 --> Contains some measure errors (real case)
2. datosMarcacionesES_1733999425626 --> Does not contains measure errors

Post can help to understand code `https://medium.com/@gomezbarrosojavier/emitter-signal-geolocation-with-machine-learning-59b377ee2145`
