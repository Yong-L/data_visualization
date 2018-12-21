
def loadData():
    """
    Load reviews from ios_reviews.json and android_reviews.json
    """

    import os
    import pandas as pd
    import json
    cur_dir = os.path.dirname(__file__)
    ios_reviews = json.load(open(os.path.join(cur_dir, 'ios_reviews.json'),
                                 'r'))
    android_reviews = json.load(open(os.path.join(cur_dir,
                                                  'android_reviews.json'), 'r'))

    dfIOS = pd.DataFrame(((app, review['rating'], review['review'])
                          for app,reviews in ios_reviews.items()
                          for review in reviews), columns=['name', 'rating', 'content'])
    dfAndroid = pd.DataFrame(((app, review['rating'], review['review'])
                              for app,reviews in android_reviews.items()
                              for review in reviews), columns=['name', 'rating', 'content'])

    return {'ios': dfIOS, 'android': dfAndroid}

def showRatingDistribution(data, name=''):
    """Create an interaactive visualization showing the distribution of ratings

    Args:
        data (DataFrame): the input data frame that must at least consists
            two columns 'name' and 'rating' for app names and ratings.
        name (str): the name of the platform (optional) to be displayed.

    Return:
        Chart: an Altair chart object that corresponds to the visualization
    """
    import altair as alt
    ## The color expression for highlighting the bar under mouse
    color_expression    = "highlight._vgsid_==datum._vgsid_"
    color_condition     = alt.ConditionalPredicateValueDef(color_expression, "SteelBlue")

    ## There are two types of selection in our chart:
    ## (1) A selection for highlighting a bar when the mouse is hovering over
    highlight_selection = alt.selection_single(name="highlight", empty="all", on="mouseover")

    ## (2) A selection for updating the rating distribution when the mouse is clicked
    ## Note the encodings=['y'] parameter is needed to specify that once a selection
    ## is triggered, it will propagate the encoding channel 'y' as a condition for
    ## any subsequent filter done on this selection. In short, it means use the data
    ## field associated with the 'y' axis as a potential filter condition.
    rating_selection    = alt.selection_single(name="rating", empty="all", encodings=['y'])

    ## We need to compute the max count to scale our distribution appropriately
    maxCount            = int(data['rating'].value_counts().max())

    ## Our visualization consists of two bar charts placed side by side. The first one
    ## sorts the apps by their average ratings as below. Note the compound selection
    ## that is constructed by adding the two selections together.
    barMean = alt.Chart() \
        .mark_bar(stroke="Black") \
        .encode(
            alt.X("mean(rating):Q", axis=alt.Axis(title="Rating")),
            alt.Y('name:O', axis=alt.Axis(title="{} App Name".format(name)), 
                  sort=alt.SortField(field="rating", op="mean", order='descending')),
            alt.ColorValue("LightGrey", condition=color_condition),
        ).properties(
            selection = highlight_selection+rating_selection,
        )

    ## The second one uses the selected app specified by the rating_selection
    ## to filter the data, and build a histogram based on the ratings. Note
    ## the use of rating_selection.ref() as a condition for transform_filter().
    ## The scale was explicitly constructed for the X axis to fill out the 
    ## the potential empty values, e.g. no one gave an app a score of 3, but
    ## we still want to show 1, 2, 3, 4, and 5 in the axis (but not in with .5).
    barRating = alt.Chart() \
        .mark_bar(stroke="Black") \
        .encode(
            alt.X("rating:O", axis=alt.Axis(title="Rating"),
                  scale=alt.Scale(type='band', domain=list(range(1,6))),
                 ),
            alt.Y("count()", axis=alt.Axis(title="Number of Ratings"),
                  scale=alt.Scale(domain=(0,maxCount)),
                 ),
            alt.ColorValue("LightGrey"),
        ).properties(
            selection = highlight_selection,
        ).transform_filter(
            rating_selection.ref()
        )

    ## We just need to concatenate the plots horizontally, and return the result.
    return alt.hconcat(barMean, barRating,
        data=data,
        title="{} App Ratings".format(name)
    )
