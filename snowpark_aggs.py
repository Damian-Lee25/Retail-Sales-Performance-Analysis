def main(session: snowpark.Session): 
    tableName = 'PUBLIC.SOURCE'
    df = session.table(tableName)

    #Print a sample of the dataframe to standard output.
    df.show()
    #Return value will appear in the Results tab.
    return df

# 5.1 Product Sales Leaderboard
# Goal: Identify which products generate the highest revenue
    
def main(session: snowpark.Session): 
    tableName = 'PUBLIC.SOURCE'
    df = session.table(tableName)
    Sales_by_Product = df.group_by('PRODUCT').agg(sum('SALES').as_('TOTAL_REVENUE')).sort(col('TOTAL_REVENUE').desc())
    return Sales_by_Product

5.2 Regional Sales Comparison
Goal: Understand how each region performs in terms of total sales

def main(session: snowpark.Session): 
    tableName = 'PUBLIC.SOURCE'
    df = session.table(tableName)
    Sales_By_Region = df.group_by('REGION').agg(sum('SALES').as_('TOTAL_REVENUE')).sort(col('TOTAL_REVENUE').desc())
    return Sales_By_Region

# 5.3 Monthly Trend Analysis
# Goal: Spot seasonal patterns and monthly performance trends

def main(session: snowpark.Session): 
    tableName = 'PUBLIC.SOURCE'
    df = session.table(tableName)
    Monthly_Trend = (df.group_by(to_varchar(col("DATE"), 'Month').alias("MONTH_NAME")).agg(sum(col("SALES")).alias("TOTAL_SALES")).sort(col("MONTH_NAME")))    
    return Monthly_Trend

# #5.4 Units Sold vs Revenue
# #Goal: Discover if high volume always translates to high revenue

def main(session: snowpark.Session): 
    tableName = 'PUBLIC.SOURCE'
    df = session.table(tableName)
    Product_Summary = (df.group_by(col("PRODUCT")).agg(
              sum(col("UNITS_SOLD")).alias("TOTAL_UNITS"),
              sum(col("SALES")).alias("TOTAL_REVENUE"))
              .sort(col("TOTAL_REVENUE").desc()))
    return Product_Summary

# 5.5 Average Order Value (AOV)
# Goal: Estimate how much value each unit sale typically generates

def main(session: snowpark.Session): 
    tableName = 'PUBLIC.SOURCE'
    df = session.table(tableName)
    
    total_summary = df.agg(
        sum(col("SALES")).alias("TOTAL_SALES"),
        sum(col("UNITS_SOLD")).alias("TOTAL_UNITS")
    )
    total_summary = total_summary.with_column(
        "AOV", col("TOTAL_SALES") / col("TOTAL_UNITS")
    )

    return total_summary