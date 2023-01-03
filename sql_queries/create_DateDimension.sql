-- Create a table to permanently store the output
CREATE TABLE
    DateDimension AS
    -- Initiate the recursive loop
WITH RECURSIVE
    -- Define a CTE to hold the recursive output
    rDateDimensionMinute (CalendarDateInterval) AS (
        -- The anchor of the recursion is the start date of the date dimension
        SELECT
            datetime ('2015-01-01 00:00:00')
        UNION ALL
        -- The recursive query increments the time interval by the desired amount
        -- This can be any time increment (monthly, daily, hours, minutes)
        SELECT
            datetime (CalendarDateInterval, '+24 hour')
        FROM
            rDateDimensionMinute
            -- Set the number of recursions
            -- Functionally, this is the number of periods in the date dimension
        LIMIT
            10000
    )
    -- Output the result set to the permanent table
SELECT
    CalendarDateInterval,
    datetime (CalendarDateInterval, '+86399 second') CalendarDateIntervalEnd,
    date (CalendarDateInterval) Date,
    strftime ('%w', CalendarDateInterval) DayNumber,
    case cast(strftime ('%w', CalendarDateInterval) as integer)
        when 0 then 'Sunday'
        when 1 then 'Monday'
        when 2 then 'Tuesday'
        when 3 then 'Wednesday'
        when 4 then 'Thursday'
        when 5 then 'Friday'
        when 6 then 'Saturday'
    end DayOfWeek,
    substr (
        'SunMonTueWedThuFriSat',
        1 + 3 * strftime ('%w', CalendarDateInterval),
        3
    ) DayOfWeekAbbr,
    strftime ('%d', CalendarDateInterval) DayOfMonth,
    case cast(strftime ('%w', CalendarDateInterval) as integer)
        when 0 then 1
        when 6 then 1
        else 0
    end IsWeekend,
    case cast(strftime ('%w', CalendarDateInterval) as integer)
        when 0 then 0
        when 6 then 0
        else 1
    end IsWeekday,
    strftime ('%m', CalendarDateInterval) MonthNumber,
    case strftime ('%m', date (CalendarDateInterval))
        when '01' then 'January'
        when '02' then 'Febuary'
        when '03' then 'March'
        when '04' then 'April'
        when '05' then 'May'
        when '06' then 'June'
        when '07' then 'July'
        when '08' then 'August'
        when '09' then 'September'
        when '10' then 'October'
        when '11' then 'November'
        when '12' then 'December'
        else ''
    end MonthName,
    case strftime ('%m', date (CalendarDateInterval))
        when '01' then 'Jan'
        when '02' then 'Feb'
        when '03' then 'Mar'
        when '04' then 'Apr'
        when '05' then 'May'
        when '06' then 'Jun'
        when '07' then 'Jul'
        when '08' then 'Aug'
        when '09' then 'Sep'
        when '10' then 'Oct'
        when '11' then 'Nov'
        when '12' then 'Dec'
        else ''
    end MonthAbbr,
    strftime ('%Y', CalendarDateInterval) YearNumber
FROM
    rDateDimensionMinute;
