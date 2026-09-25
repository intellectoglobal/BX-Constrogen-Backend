INSERT INTO "builder-iq"."APTerms" ("APTerm_Key", "APTerm_ID", "APTerm_Descr", "APTerm_Days", "APTerm_CreatedBy", "APTerm_CreatedDtTm", "APTerm_LastModifiedBy", "APTerm_LastModifiedDtTm", "APTerm_Company_ID", "APTerm_Client_ID")
VALUES 
    (1, '30D-Inv', '30 Days from Invoice Date', 30, 'bis', '2022-08-06 06:00:42.95393', 'Prem', '2023-01-02 12:27:28', 28, 1),
    (2, '60D-Inv', '60 Days from Invoice Date', 60, 'bis', '2022-08-06 06:00:42.95393', 'rahulr001', '2023-01-12 18:08:11', 28, 1),
    (5, '90D-Inv', '90 Days from Invoice date', 90, 'Prem', '2022-12-22 07:42:07', 'rahulr001', '2023-01-12 18:08:31', 28, 1),
    (10, '30-D', '30-Days', 30, 'rahulr001', '2023-01-16 19:18:31', NULL, NULL, 25, 4),
    (13, 'APTerms_1', 'Monthly', 31, 'Prem', '2023-01-28 17:08:54', 'Prem', '2023-02-21 16:46:45', 1, 5),
    (14, 'APTerms_2', 'Week', 7, 'Prem', '2023-01-28 17:08:54', 'Prem', '2023-02-21 16:46:34', 1, 5),
    (15, 'APTerms_3', 'Annual', 365, 'PerfectSenthil', '2023-01-28 17:08:54', 'Prem', '2023-02-21 16:46:20', 1, 5),
    (16, 'APTerms_4', 'Daily', 1, 'PerfectSenthil', '2023-07-01 07:17:51', NULL, NULL, 1, 5),
    (17, 'APTerms_5', 'Flexible', 0, 'PerfectSenthil', '2023-07-01 07:17:51', NULL, NULL, 1, 5);
