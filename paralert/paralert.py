import pandas as pd
import json
import math
import yaml
import urllib.request


def get_paraglidable_json():
    
    response = requests.get("https://api.paraglidable.com/?key=d60092fb1105a1f4&format=JSON&version=1")
    forecast_pgble = json.loads(response.text)
    forecast_pgble = json.dumps(forecast_pgble, sort_keys=True, indent=4)
#    print(forecast_pgble)
          
    write_to_JSON_file('./paraglidable_forecast/', 'forecast_pgble', forecast_pgble)


def write_to_JSON_file(path, fileName, data):
    
    filePathNameWExt = './' + path + '/' + fileName + '.json'
    with open(filePathNameWExt, 'w') as fp:
        json.dump(data, fp)


def add_windspeed_winddir_to_forecast(forecast_df):
    """
    Add wind speed and wind direction lists to a forecast DataFrame.

    Args:
        forecast_df (DataFrame): Forecast dataframe

    Returns:
        -
    """
    windspeed_column = forecast_df.apply(
        lambda row: [
            3.6 * math.sqrt(u**2 + v**2)
            for u, v in zip(row["umet"], row["vmet"])
        ],
        axis=1,
    )
    winddir_column = forecast_df.apply(
        lambda row: [
            math.atan2(u, v) * 180 / math.pi - 90
            for u, v in zip(row["umet"], row["vmet"])
        ],
        axis=1,
    )
    forecast_df["wspd"] = pd.Series(windspeed_column, index=forecast_df.index)
    forecast_df["wdir"] = pd.Series(winddir_column, index=forecast_df.index)


def filter_out_low_cloudbase(forecast_df, min_bl_thickness):
    """
    Filters columns of a forecast DataFrame, where the boundary
    layer thickness is less than min_bl_thickness.

    Args:
        forecast_df (DataFrame): Forecast dataframe
        min_bl_thickness (int): Minimum thickness of the boundary layer

    Returns:
        DataFrame: Filtered-out DataFrame
    """
    return forecast_df[forecast_df["pblh"] >
                       (forecast_df["ter"] + min_bl_thickness)]


def filter_out_strong_wind(forecast_df, max_windspeed):
    """
    Filters columns of a forecast DataFrame, where the wind speed
    exceeds max_windspeed

    Args:
        forecast_df (DataFrame): Forecast dataframe
        max_windspeed (int): Maximum windspeed

    Returns:
        DataFrame: Filtered-out DataFrame
    """
    return forecast_df[forecast_df.apply(
        lambda row: max(row["wspd"]) < max_windspeed, axis=1
    )]


def get_flight_score(forecast_df):
    """
    Filters columns of a forecast DataFrame, where the wind speed
    exceeds max_windspeed

    Args:
        forecast_df (DataFrame): Forecast dataframe
        max_windspeed (int): Maximum windspeed

    Returns:
        DataFrame: Filtered-out DataFrame
    """
    return forecast_df.sum(axis = 0)["pblh"]


if __name__ == "__main__":
    
    get_paraglidable_json()
    
    with open("forecast.json", "r") as f:
        json_data = json.load(f)

    with open("locations.yaml", "r") as f:
        locations = yaml.load(f)

    site_parameters = locations["gensac"]
    print(site_parameters)

    forecast_df = pd.DataFrame(json_data["data"]).transpose()
    add_windspeed_winddir_to_forecast(forecast_df)
    print(forecast_df)

    forecast_df = filter_out_low_cloudbase(
        forecast_df, site_parameters["min_bl_thickness"]
    )
    print(forecast_df)

    forecast_df = filter_out_strong_wind(
        forecast_df, site_parameters["max_windspeed"]
    )
    print(forecast_df)

    print(get_flight_score(forecast_df))
