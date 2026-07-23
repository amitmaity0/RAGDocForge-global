
## Summary

How to retrieve General Ledger Interface error codes in Oracle R12?

## Solution

In Oracle R12, error codes related to the General Ledger (GL) Interface are stored in specific database tables.  
The GL_INTERFACE table stores GL interface records, including those with errors. The error codes are referenced in the FND_LOOKUPS table under the lookup type PSP_SUSP_AC_ERRORS.

Use the following SQL query to fetch error details for GL interface records:
```
SELECT  
gi.status AS error_code,  
fl.meaning AS error,  
fl.description AS error_desc,  
gi.*  
FROM  
apps.gl_interface gi,  
apps.fnd_lookups fl  
WHERE  
gi.status = fl.lookup_code  
AND fl.LOOKUP_TYPE = 'PSP_SUSP_AC_ERRORS'  
AND gi.ledger_id = &ledger_id;
```
Parameters:

ledger_id: Replace with the appropriate ledger ID to filter results for a specific ledger.

## References

MOS document id: 3076451.1


## Summary

This FAQ provides the answers for the most common questions about Journal Import.  
  
Technical briefs also provide a useful insight into the topic. Please refer to the following:  Note:KB625770  General Ledger: Journal Import Process.  
  
If you are receiving errors or having problems related to Journal Import then it is recommended to use the  Note:330821.1 Journal Import Troubleshooting Guide  
  
Questions regarding usage, functional clarification, general information, documentation or functionality of the Oracle General Ledger product will receive the fastest response (generally real time to 24hrs timeframe) if they are posted on the My Oracle Support Community for Oracle E-Business Suite General Ledger.  
This is monitored on a daily basis by Oracle Support Services (OSS) with the highest importance. Discussion threads often receive multiple responses from other users and/or consultants on questions and issues.  
OSS is strongly recommending that issues of this nature be posted on the Oracle E-Business Suite General Ledger Community.

## Details

### 1. What is Group ID used for?

> The Group ID distinguishes data to import within a particular source, i.e. Oracle Receivables, Payables or other subledgers / legacy systems.  
> Since minipack 11i.GL.D (or with Patch: 1455528) the Journal Import Submission form can select "All Group Ids" from a particular source.  
>   
> The same does not happen for Standard Report Submission for Journal Import , where a specific group_id (or null group_id) must be specified.  
>   
> When a subledger does not populate the group_id (null) then it may occur that different batches from the same source are merged by the first Journal Import process meeting the criteria.  
> If the Journal Import is automatically submitted by the subledger, and several users are transferring to GL at the same time, then some of the processes may get the 'No Data Found' error, because the expected lines were already imported by the first process. This does not happen if the group_id is used.

### 2. Can Reversals be automatically generated?

> Journal Import does not automatically create reversing journal entries.  
>   
> If the reversal flag and reversal period were populated in the GL_INTERFACE table, then the reversal must be generated after Journal Import is run.  
>   
> In 11i the Autoreversal procedure can be setup to create reversing Journals automatically once an imported journal is created.

### 3. How is the Effective Date derived?

> Journal Import will store the value for the DEFAULT_EFFECTIVE_DATE in GL_JE_HEADERS picked from one of the accounting dates in GL_INTERFACE lines.  
> It will be the first line that appears on the journal under that header.  
> This is decided by the values in the code combination and is arbitrary from a financial point of view although treated consistently for each journal header in a batch.  
>   
> All the journal headers within a batch may not have the same default effective date when imported in SUMMARY mode but all the lines will match the header for that journal.  
> If you wish the lines to have different effective dates then do not use the Create Summary Journals option.  
>   
> Exceptions:  
> If you use Average Daily Balances (ADB) this behaviour is different.  
> If you have the new profile option: GL Journal Import: Separate Journals by Accounting Date, journal import will only group together journal lines that have the same date, while lines with different effective dates will be put under different journal headers even if they belong to the same period.  
> This is available on 11.5.10 family pack 11i.FIN_PF.E.

### 4. How is the GL Batch Name derived?

> The batch name uses the first 50 characters from REFERENCE1 in GL_INTERFACE (if populated) followed by:  
> - Source  
> - Request ID  
> - Actual Flag  
> - Group ID  
> In Consolidation journals, the profile option GL Consolidation: Preserve Journal Batching set to Yes will preserve up to 50 characters of the original batch name plus batch ID in the source set of books to the target set of books.

### 5. How is the Period determined?

> Journal Import selects the period corresponding to the ACCOUNTING_DATE populated in GL_INTERFACE.  
>   
> Then the imported lines are grouped by period and the Journal Entry is created with the ACCOUNTING_DATE of the last calendar day of the period.  
>   
> Prior to 11i.GL.F the contents of the PERIOD_NAME column in the GL_INTERFACE table is ignored, therefore it is not possible to import for adjusting periods.  
> After 11i.GL.F the behavior has changed to allow Journal Import to import data into adjustment periods, for that purpose the PERIOD_NAME is used in combination with the ACCOUNTING_DATE.  
>   
> Journal Import groups lines with the same Period into the same journal, even if the lines have different Accounting Dates, for all sets of books except:  
> - the set of books is an Average Daily Balances set of books  
> - the profile option GL Journal Import: Separate Journals by Accounting Date is set to YES  
>   
> In these cases it would put lines with different Accounting Dates into separate journals.

### 6. How to import journals for Adjusting Periods?

> Before 11i.GL.F it is not possible to import journals directly for adjusting periods. The selected period is the regular period corresponding to the effective date calculated.  
>   
> The workaround for this is to import for a regular period and, before posting, use Change Period function on the Enter Journals form.  
>   
> Since 11i.GL.F the behavior has changed to allow Journal Import to import data into adjustment periods and also to import data that is to be reversed into adjustment periods.  
> For budgets the PERIOD_NAME column in the GL_INTERFACE table will now be able to hold both adjustment and non-adjustment periods.  
> For actual and encumbrance data the period that the data will be imported to will now be controlled by a combination of the ACCOUNTING_DATE and the PERIOD_NAME:  
> - if a valid period name is specified and that period contains the accounting date then that period is used;  
> - otherwise the non-adjusting period that contains the accounting date is used  
> The REFERENCE8 column in the GL_INTERFACE table will now be able to hold both adjusting and non-adjusting reversal periods or reversal date for Average Balance data.

### 7. Subledger transactions were transferred but are missing in GL

> The transfer from the subledger could be successful, but the journals may have errored out in Journal Import, leaving the transactions in GL_INTERFACE table.  
>   
> Check the Journal Import Execution report for any possible validation errors and the Journal Import log file for execution errors.  
> In that case the journals would not be seen neither in the Posting form nor the Enter Journals form, but would be available on the Journal Import Correct form.  
>   
> You can also check the contents of the GL_INTERFACE table by running the simple SQL in  Note:KB737745.  
> If the transactions are in GL_INTERFACE then you need to correct them and re-run Journal Import . See  [Note:1056801.6](https://support.oracle.com/rs?type=doc&id=1056801.6 "1056801.6")  for more information.  
>   
> If the journals are still not found, verify that the responsibility you are using does not have security rules that would prevent you from viewing the data.  
>   
> See also  KB713048  Journal Import Troubleshooting Guide

### 8. Create Summary Journals: what is the advantage of using it?

> Importing journals using this run option selected will summarize all transactions for the same period, account and currency, into one debit/credit journal line.  
>   
> This will make your reports more manageable in size, but you lose the one to one mapping of your detail transactions to the summary journal lines created by Journal Import.  
> You can still maintain a mapping of how Journal Import summarizes your detail transactions from your feeder systems into journal lines, if the Journal Source definition has the Import Journal References option checked.

### 9. Can Descriptive Flexfield be Imported?

> Yes. Descriptive Flexfields can be imported with or without validation.  
> The Descriptive Flexfields that can be imported via Journal Import are the ones that map to the reference fields of the GL_JE_LINES table.  
>   
> There are 3 options for Descriptive Flexfields (DFF) import:  
> - No: DFF information will be ignored by GL.  
> - With Validation: Journal Import generates journals only if DFF are valid.  
> - Without Validation: the DFF information is imported into GL as it is, without any validation.  
>   
> See  [Note:1062015.6](https://support.oracle.com/rs?type=doc&id=1062015.6 "1062015.6")  and  Note:KB747325  for more information.

### 10. Rollback Segment: can this be modified?

> There is no option available for Journal Import to choose the Rollback Segment.  
> There is a setup option available for the Number Of Lines to Process at Once that affects Journal Import.  
>   
> Navigation: Setup > System >Controls.

### 11. Can Journal Import be Automated or included in a request set?

> The Journal Import Program (GLLEZLSRS) is a new functionality included in 11.5.10 which allows the submission of journal import from the standard report submission screen like any normal concurrent process.  
> Therefore it can also be scheduled or included in a Report Set.  
> However it is currently limited to specific or NULL group_ids, the 'All Group IDs' option does not exist. See  Note:KB750810  for more information.  
>   
> It is also possible to use the CONCSUB utility to submit a Journal Import from outside of the application and create batch jobs to automatically run the Journal Import. However this process needs to receive, as a parameter, the value of the GL_INTERFACE_CONTROL.INTERFACE_RUN_ID column.  
>   
> For more information on CONCSUB see the Oracle Applications System Administrator's Guide.  
> See also  [Note:1079972.6](https://support.oracle.com/rs?type=doc&id=1079972.6 "1079972.6"),  [Note:198041.1](https://support.oracle.com/rs?type=doc&id=198041.1 "198041.1")  for more information .  

### 12. How to improve Performance?

> There may be different causes for a bad performance in Journal Import process.  
>   
> If you have a general poor performance in Journal Import then please follow the recommendations from  Note:KB626741  How to Improve Journal Import Performance and Performance of Other GL Programs in 11i  
>   
> If the performance problem only occurs for high volume batches then review  Note:KB738781  GLLEZL: Problems Importing Very Large Journal Batches  
>   
> Specific patches effecting Journal Import Performance:  
> Patch:1455528: Multi-Table Journal Import  
> Patch:2608405: GLLEZL SIGNAL 11 When a GROUP_ID has a huge number of lines in GL_INTERFACE  
> Patch:2717598: The records with the STATUS 'PROCESSED' in GL_INTERFACE remain forever...  
> Patch:3087842: The records with the STATUS 'PROCESSED' in GL_INTERFACE remain  
> Patch:3535059: APPSPERF:GL: GLLEZL not using BIND variables

### 13. Where to check for the Error Messages (Status codes)?

> The Journal Import automatically generates the Journal Execution Report with information about the created journals.  
> If validation errors are detected then the exception lines with the respective error codes are also listed. The final section of the report is a complete list of validation error codes and their meanings.  
> See  [1056801.6](https://support.oracle.com/rs?type=doc&id=1056801.6 "1056801.6")  for a list of these errors.  
>   
> If Patch: 2162483: Enhancement to provide Warning Statuses for Journal Import, is installed then Journal Import will end in a warning status in the following cases:  
> - When no data matching the specified criteria is found in the GL_INTERFACE table.  
> - When data is not imported successfully.  
> - When data is imported with a warning.  
>   
> Some unexpected execution errors may also occur. Those are shown in the log file and the process is terminated in error.

### 14. Can lines be deleted from GL_INTERFACE?

> Yes, lines from GL_INTERFACE can be deleted.  
> However, this procedure is not recommended, as data originating in the subledger / feeder system may be lost or no longer retrievable.  
> The Correct Journal Import Data form should be used to correct Journal Import errors. You should also refer back to the subledgers where the data originated.  
> This form can only be used to delete batches with lines that have already been processed and rejected in error. If no Group ID is selected only lines with GROUP_ID as NULL will be deleted.

### 15. How to check the contents of the GL_INTERFACE table?

> Run the sql statement below for a summary of the GL_INTERFACE contents.  
> It will give an idea of the batches waiting to be imported.  
>   
> 
> select  
> set_of_books_id, user_je_source_name, actual_flag, group_id,  
> period_name, status, request_id, sum(nvl(accounted_dr,0)),  
> sum(nvl(accounted_cr,0)), count(*)  
> from gl_interface  
> group by set_of_books_id, user_je_source_name,  
> actual_flag, group_id, period_name, status, request_id
> 
> See  KB737745  for more information

### 16. How to correct Validation Errors in the GL_INTERFACE table?

> Validation errors usually mean that the data populated in the interface table is incorrect, for instance an undefined period, or that General Ledger is not ready to receive those journals, for instance the receiving period is not Open.  
>   
> See  [1056801.6](https://support.oracle.com/rs?type=doc&id=1056801.6 "1056801.6")  for a list of these errors.  
>   
> The corrective actions to fix the errors may depend on the error code and on the source of the transactions.  
>   
> The Correct Journal Import Data form can be used to manually correct the lines with a status error in GL_INTERFACE table. However this does not fix the data in the subledger / feeder system.  
>   
> See  KB713048  Journal Import Troubleshooting Guide, for more information

### 17. What are the primary GL tables updated by Journal Import?

> The primary GL tables populated during Journal Import are:  
>   
> - GL_JE_BATCHES  
> - GL_JE_HEADERS  
> - GL_JE_LINES  
> - GL_IMPORT_REFERENCES (link to source transactions)  
> - GL_INTERFACE_HISTORY (optional)  
> - GL_BC_PACKETS (budgetary control)

### 18. Are Cross-Validation or Security Rules validated?

> Journal Import does not check for Security Rules. It is the feeder system that must validate the account code combinations populated in GL_INTERFACE table.  
>   
> You can also populate the accounting segments directly into the gl_interface table and let Journal Import populate the code_combination_id. If dynamic insertion is enabled, and this is a new combination, then the import program will check for cross validation rule violations.

### 19. Community Discussions

Still have questions? Use the _live_  [My Oracle Support General Ledger Community](https://community.oracle.com/community/support/oracle_e-business_suite/general_ledger) to search for similar discussions or start a new discussion on this subject.

### Feedback

To provide feedback on this note, click on the  **Rate this document**  link.

## References

MOS document id: 342391.1


## Summary

This troubleshooter can provide a solution for some of the most frequent problems related to General Ledger (GL) Journal Import functionality.  
  
You may also wish to check  FAQ7054  General Ledger Journal Import FAQ  
  

### About Journal Import

Journal Import, sometimes also called EZLINK or EASYLINK, is the process which creates General Ledger Journal Entries for the Accounting transactions that originated as a result of normal business activities in Financial and Manufacturing modules of Oracle Applications, as well as in external and legacy modules.

1.  Each subledger populates the GL_INTERFACE table using their own specific process. Some can automatically launch the Journal Import program.
2.  The Journal Import process validates the data in the the GL_INTERFACE table and loads the validated data into General Ledger tables, creating unposted batches.
3.  If the data is invalid it will not be imported and will stay in the GL_INTERFACE table, flagged with an error label, waiting for corrective actions or deletion.
4.  After correction of the errored lines, Journal Import can be submitted again.
5.  At the end of the process, the lines successfully imported are deleted from the interface table.
6.  The Journal Import process generates the Journal Import Execution report with a summary of the Journals successfully created and a summary of the batches with validation errors.  
    A log file showing possible execution errors is also produced.

Please note that if you are using the Multi-Table Journal Import feature, the references to the GL_INTERFACE table must be changed to the interface table name you are using.  
  

## Solution

### **A) Form GLXJIRUN: Import Journals**

  
Run the sql statement below for a summary of the GL_INTERFACE contents.  
It will give an idea of the batches waiting to be imported and the results can be used to help diagnose the issue.

> select set_of_books_id, user_je_source_name, actual_flag,  
> group_id, period_name, status, request_id,  
> sum(nvl(accounted_dr,0)) DR, sum(nvl(accounted_cr,0)) CR, count(*)  
> from gl_interface  
> group by set_of_books_id, user_je_source_name, actual_flag,  
> group_id, period_name, status, request_id

### A-1) FRM-41830: List of values contains no entries for Group_id

> The GROUP_ID List of Values returns the error:  
> - FRM-41830: List of values contains no entries.  
>   
> This problem can have 3 different causes.  
> The results of the previous script will help to distinguish the cause and the fix.  
>   
> 1. The transactions from the specified SOURCE have no GROUP_ID populated (is NULL).  
> For example the Receipt Accruals - Period-End Process does not populate the field Group_id.  
> - In this case the No Group Id option must be selected.  
>   
> 2. The set_of_books_id in GL_INTERFACE is not the same assigned to the responsibility.  
> - Either a different responsibility needs to be used or the set_of_books_id must be fixed in GL_INTERFACE.  
>   
> 3. A previous Import run for the same lines was aborted or terminated in error.  
> - The GROUP_ID must be entered manually without using the LOV.  
>   
> See  [1082995.6](https://support.oracle.com/rs?type=doc&id=1082995.6 "1082995.6")  for more information.

### A-2) FRM-40212: Invalid value for field Group_id

> Entering the GROUP_ID value returns the error:  
> - FRM-40212: Invalid value for field GROUP_ID.  
>   
> The results from the previous script will help to confirm that the set_of_books_id in GL_INTERFACE is not the same assigned to the responsibility.  
>   
> Either:  
> a different responsibility needs to be used (check the profile option GL: Set of Books)  
> or  
> the set_of_books_id must be fixed in GL_INTERFACE.  
>   
> See  [1082995.6](https://support.oracle.com/rs?type=doc&id=1082995.6 "1082995.6")  for more information

### A-3) APP-00268: Please specify a valid printer

> Clicking the Import Button for a 'Spreadsheet' source returns the error message:  
> - APP-00268: Please specify a valid printer.  
>   
> Either:  
> assign a valid printer to the profile option Printer  
> or  
> uncheck the Print option for the Concurrent Program GLLEZL.  
>   
> See  [99231.1](https://support.oracle.com/rs?type=doc&id=99231.1 "99231.1")  for more information.

### A-4) Cannot select some Batches with previous import errors

> Some Journal Batches are Stuck in Processing Status and can not be selected to import.  
> The Source field and/or the Group_id lists of values are not showing the values wanted to import.  
>   
> This is caused by a previous Journal import process that was aborted or ended with a severe error usually caused by an Ora-01652: unable to extend temp segment.  
> The results from previous script can help to confirm this situation - check the existent request_id value.  
> The GL_INTERFACE_CONTROL table is used to control Journal Import execution. There is one row in this table for each journal entry source.  
> If the status is not 'P' it means that the source is not available to import (it is either selected or in process).  
> When the process was interrupted the status was not reset to 'P'.  
>   
> Confirm that the process is not running and run the following update:  
> 
> > > Update gl_interface_control  
> > > set status = 'P'  
> > > where group_id = &group_id  
> > > and interface_run_id = &request_id;
> > 
> > if only 1 line updated then:  
> > 
> > > commit;
> > 
> > otherwise:  
> > 
> > > rollback;
> 
>   
> Now the Batch can be submitted.

### A-5) The 'All Group_ids' option is missing

> The GROUP_ID List of Values does not show the All Group Ids option.  
>   
> This option is introduced by Patch:1455528, which delivers form GLXJIRUN.fmb version 115.10.  
> It is included since Mini-pack 11i.GL.F.

### A-6) The Group_id default value changed to All Group Ids

> The default value in the GROUP_ID List of Values has changed to All Group Ids instead of No Group Id.  
>   
> Problem fixed in GLXJIRUN.fmb version 115.12 delivered by one-off Patch:3176768.  
> It is included on Financials Family Pack 11i.FIN_PF.E.

### A-7) Labels with garbage Arabic characters

> Problem fixed in GLXJIRUN.fmb version 115.10 delivered by one-off Patch:2375269.  
> This is a specific NLS Arabic patch for this file version.

----------

### **B) Standard Report Submission for Journal Import (SRS)**

The Journal Import Program (GLLEZLSRS) is a new functionality included in 11.5.10 which allow the submission of journal import from the standard report submission screen like any normal concurrent process.

B-1) GLLEZLSRS errors with FND-CANNOT FIND FILE

> Submitting the Journal import standard request submission - GLLEZLSRS and it ends in error:  
> 
> > _FND-CANNOT FIND FILE_  
> > _Concurrent Manager encountered an error while running SQL*Plus for your concurrent request #######_
> 
> Install Patch:3386758 - Enhancement: Allow Journal Import To Be Submitted Through Srs

### B-2) Missing option 'All Group IDs' in GLLEZLSRS program parameters

> When submitting the 'Program- Import Journals' (GLLEZLSRS) there is not the option to select All Groups IDs in the report parameters.  
> The only available options are to enter a specific Group ID number or leave blank. Leaving it blank will only select data with no group ID.  
>   
> There is no solution. This is expected functionality.  
>   
> See <Document 316515.1 > for more information.  
> There is already an enhancement request Bug:4561025 logged for this, but it is still unknown if or when it will be delivered.

----------

### **C) GLLEZL errors during the Journal Import execution**

Problems occurring during the execution of Journal Import program (GLLEZL) usually do not create GL journal entries, and the lines remain in the interface table to be re-imported after correction or to be discarded.  
  
This program automatically generates the Journal Execution Report with information about the created journals.  
If validation errors are detected then the exception lines with the respective error codes are also listed.  
The final section of the report is a complete list of validation error codes and their meanings.  
  
If Patch:2162483: Enhancement to provide Warning Statuses for Journal Import, is installed then Journal Import will end in a warning status in the following cases:  
1. When no data matching the specified criteria is found in the GL_INTERFACE table.  
2. When data is not imported successfully.  
3. When data is imported with a warning.  
Some unexpected execution errors may also occur. Those are shown in the log file and the process is terminated in error.

### **C-1) Import Validation Errors**

Validation errors usually mean that the data populated in the interface table is incorrect, for instance an undefined period, or that General Ledger is not ready to receive those journals, for instance the receiving period is not Open.  
  
An example of the error list can be viewed [here]. This list may not be complete as new error codes are incorporated when new functionalities or validation rules are added to the Journal Import program.  
  
The corrective actions to fix these errors may depend on the error code and on the source of the transactions.  
  
Considering the data in the source system choose one of the situations:

### C-1.1) Interface Data is Correct:

> If you have verified that the interface data is correct but the Journal Import has found a validation error then you need to review the General Ledger setup to find the reason why the data is not being accepted and fix it. The most common cause is related to Period Error Codes EPnn.

### C-1.2) Source system data can be fixed and re-transferred

> If the data in Interface table is incorrect then most probably it is also incorrect on the source system (feeder).  
> If this is the case then the data in the source system or application must be identified and fixed. After having deleted the error batch in the interface table then the source data must be re-transferred.  
> If the source system is an Oracle Sub-Ledger (like Payables, Receivables, Purchasing, etc.) then please use My Oracle Support to log a Service Request for the specific product support team.

### C-1.3) Source system data cannot be fixed and/or re-transferred

> If the source system data is correct (only the interface data is incorrect) or is impossible to fix and transfer again to the interface, then the interface lines with error status must be corrected, using the Correct Journal Import Data form, so they can be imported into GL.  
>   
> Keep in mind that only the lines marked with an error status can be retrieved in the Correct Journal Import Data form.  
> The lines from the same batch but having no validation errors will get a status of 'P' and will not be retrieved in the Correct Journal Import Data form.

### **C-2) Import Execution Errors**

Review the Log File of the Journal Import process that has failed.  
Usually the problem is caused by an ORA-..... error. Try to find the first occurrence of an ORA-..... error in the log file.

### C-2.1) ORA-00054 Error in gllaar

> The Journal Import Log file shows the following error:  
> 
> Error in: gllaar  
> Function return status: 0  
> Function Err Message: unable to truncate table  
> Function warning number: -1  
> *****************************************************  
> sqlcaid: sqlabc: 0 sqlcode: 0 sqlerrml: 0  
> sqlerrmc:  
> ORA-00054: resource busy and acquire with NOWAIT specified  
> ORA-06512:
> 
> The lines were imported but were not deleted from GL_INTERFACE and stayed with Status 'PROCESSED', so they can be manually deleted from the table.  
> See  Document KB774086  for more information.  
>   
> To avoid this problem apply Patch:2717598: The records with the STATUS 'PROCESSED' in GL_INTERFACE remain forever...  
> This patch is also included on 11i.GL.I patchset.  
> Also see  [Document 235753.1](https://support.oracle.com/rs?type=doc&id=235753.1 "235753.1")  for more information

### C-2.2) ORA-00604, ORA-00904 Error in gllcje

> Journal Import Log file shows the following error:  
> 
> Error in: gllcje Function return status: 0  
> Function Err Message: Executing ins_prep using descriptor insbindda  
> Function warning number: -1  
> *****************************************************  
> sqlcaid: sqlabc: 0 sqlcode: -604 sqlerrml: 70  
> sqlerrmc:  
> ORA-00604: error occurred at recursive SQL level 1  
> ORA-00904: invalid
> 
>   
> DBA must drop the snapshots on the database.

### C-2.3) ORA-00904 Error in gllcje

> The Journal Import Log file shows the following error:  
> 
> Error in: gllcje  
> Function return status: 0  
> Function Err Message: Preparing main_prep from main_stmt  
> Function warning number: -1  
> *****************************************************  
> sqlcaid: sqlabc: 0 sqlcode: -904sqlerrml: 31  
> sqlerrmc:  
> ORA-00904: invalid column name
> 
>   
> This problem can be caused by corrupted data on GL_INTERFACE_CONTROL table.  
> If no Journal Import processes are running, truncate GL_INTERFACE_CONTROL and re-import the batches.  
> See  [223090.1](https://support.oracle.com/rs?type=doc&id=223090.1 "223090.1")  for more information

### C-2.4) ORA-00942, ORA-06512 Error in gluddl

> When importing PA transactions, the Journal Import Log file shows the following error:  
> 
> -- gluddl ad.do_ddl error buffer begin  
> do_ddl(APPLSYS, SQLGL, 20, $statement$, PA_GL_INTERFACE): private_do_ddl(APPS, APPLSYS, GL, 20, $statement$, PA_GL_INTERFACE): do_a_tab_a_seq_acd_ind(GL, $statement$): :  
> do_apps_ddl(GL, $statement$): : substr($statement$,1,255)='Truncate Table PA_GL_INTERFACE'  
> -- gluddl ad.do_ddl error buffer end  
> -- gluddl Message Dictionary Start:  
> do_ddl(APPLSYS, SQLGL, 20, $statement$, PA_GL_INTERFACE): private_do_ddl(APPS, APPLSYS, GL, 20, $statement$, PA_GL_INTERFACE): do_a_tab_a_seq_acd_ind(GL, $statement$): :  
> do_apps_ddl(GL, $statement$): : substr($statement$,1,255)='Truncate Table PA_GL_INTERFACE'  
> ORA-00942: table or view does not exist  
> ORA-06512: at "SYSTEM.AD_DDL",  
> APP-FND-01388: Cannot read value for profile option GL_JI_IGNORE_CURRENCY_DATE in routine &ROUTINE.
> 
>   
> Install Patch:2618381  
> This patch was included in Mini-Pack 11i.GL.H.

### C-2.5) ORA-01003 Error in gllcje

> The Journal Import Log file shows the following errors:  
> 
> Error in gllcje  
> Function return status: 0  
> Function Err Message: Executing upd_prep using descriptor updbindda  
> Function warning number: -1  
> ******  
> sqlcaid: sqlabc: 0 sqlcode: -1003 sqlerrml: 51  
> sqlerrmc:  
> ORA-1003: unable to open message file (SQL-2113).
> 
>   
> Navigate to Setup : System : Controls and increase the 'Number of Journal Lines to Process at Once'  
> See <Document 1015799.102> for more information

### C-2.6) ORA-01041 Error in fdfgcd

> The Journal Import terminates in error and the Log file shows the following:  
> 
> APP-FND-01564: ORACLE error 1000 in fetch_lines  
> Cause: fetch_lines failed due to ORA-01000: maximum open cursors exceeded.  
> The SQL statement being executed at the time of the error was: &SQLSTMT and was executed from the file &ERRFILE.ORACLE error 1041 in FDPCLS  
> Cause: FDPCLS failed due to ORA-01041: internal error. hostdef extension doesn't exist
> 
>   
> Navigate to Setup : System : Control and adjust the settings on the Concurrent Programs Control form to satisfy the amount of data being imported.

### C-2.7) ORA-01400 Error in gllchd

> The Journal Import Log file shows the following error:  
> 
> ORA-1400: cannot insert NULL into ("GL"."GL_JE_HEADERS"."ACCRUAL_REV_  
> SHRD0105: Gegevens worden ingevoegd in gl_je_headers ...  
> Error in: gllchd  
> Function return status: 0  
> Function Err Message: Executing hd_prep  
> Function warning number: -1  
> *****************************************************  
> sqlcaid: sqlabc: 0 sqlcode: -1400 sqlerrml: 70  
> sqlerrmc:  
> ORA-1400: cannot insert NULL into ("GL"."GL_JE_HEADERS"."ACCRUAL_REV_
> 
>   
> Problem occurs when the period name starts with '-'.  
> Apply Patch:4177513 to install gllrev.lpc version 115.8 to resolve the issue.  

### C-2.8) ORA-01403 Error in gllccl

> When importing Cross Currency Journals from sub-ledgers the Journal Import Log file shows the following error:  
> 
> gllccl_cross_currency_lines()  
> Error in: gllccl  
> Function return status: 0  
> Function Err Message: failure to get cross currency account  
> Function warning number: -1  
> ************************************************  
> sqlcaid: sqlabc: 0 sqlcode: 1403 sqlerrml: 25 sqlerrmc:  
> ORA-1403: no data found
> 
>   
> Make sure you have defined the following suspense accounts for your Set of Books and also for the Reporting Sets of Books in case you are using MRC (Multiple Reporting Currencies).

> Source
> 
> Category
> 
> Payables
> 
> Cross Currency
> 
> Receivables
> 
> Cross Currency
> 
> AP Translator
> 
> AP Subledger Entries (when AX in use)
> 
> AR Translator
> 
> AR Subledger Entries (when AX in use)
> 
>   
> These accounts need to be defined even if Suspense Posting is not checked in your set of books. The process in Journal Import checks for the creation of suspense accounts (if the journal is out of balance or is a cross currency journal), whether or not suspense posting is allowed.  
> See  [312835.1](https://support.oracle.com/rs?type=doc&id=312835.1 "312835.1")  for more information

### C-2.9) ORA-01403 Error in gllcje.gllale

> The Journal Import Log file shows the following error:  
> 
> Error in: gllcje.gllale  
> Function return status: 0  
> Function Err Message: calloc failure for ezlselda->V[27] or ezlselda->I[27]  
> Function warning number: -1  
> *****************************************************  
> sqlcaid: sqlabc: 0 sqlcode: 0 sqlerrml: 0  
> sqlerrmc:  
> ORA-01403: no data found
> 
>   
> Navigate to the Setup : System : Controls form and decrease the 'Number of Journal Rows to Process at once'.  
> See  KB719181  for more information

### C-2.10) ORA-01403 Error in gllcnt

> The Journal Import Log file shows the following error:  
> 
> Error in: gllcnt  
> Function return status: 0  
> Function Err Message: sqlerror trapped at selerr  
> Function warning number: -1  
> *****************************************************  
> sqlcaid: sqlabc: 0 sqlcode: 0 sqlerrml: 0  
> sqlerrmc:  
> ORA-01403: no data found
> 
>   
> 1. The Basic Interfund Accounting setup is not correct.  
> Change the Setting of the Profile Option: GL: Create Interfund Entries to "NO" or verify that the setup is correct for Basic Interfund Accounting.  
> See  [250465.1](https://support.oracle.com/rs?type=doc&id=250465.1 "250465.1")  for more information  
>   
> 2. Check the database for Invalid Objects. Recompile them (if any) and relink the executable.

### C-2.11) ORA-01403 Error in gllcoa

> The Journal Import Log file shows the following error messages:  
> 
> SQLERRMC ORA-01403: no data found  
> error in: gllcoafunction return status:0  
> function Err Message: fdfkfa () -FFSTSEGS-BALANCE failure message:  
> function warning number: -1
> 
>   
> The Accounting Flexfield Structure has no segment defined as balancing segment.  
> You must define only one segment with Natural Account and other with Balancing Segment qualifiers, the Cost Center qualifier is optional.  
> See <Document 1017962.102> for more information

### C-2.12) ORA-01403 Error in glldhkc

> The Journal Import Log file shows the following error:  
> 
> Error in: glldhkc  
> Function return status: 0  
> Function Err Message:  
> Function warning number: -1  
> *****************************************************  
> sqlcaid: sqlabc: 0 sqlcode: 1403 sqlerrml: 70  
> sqlerrmc:  
> ORA-01403: hiveri bulunmad?  
> ORA-06512: konum "APPS.ITG_X_UTILS", sa
> 
>   
> Please apply Patch:3981095.  
> Then use FNDLOAD to reapply this data loader file: $ITG_TOP/patch/115/import/US/itgtrade.ldt:  
>   
> FNDLOAD apps/apps 0 Y UPLOAD $FND_TOP/patch/115/import/.lct $ITG_TOP/patch/115/import/US/itgtrade.ldt - CUSTOM_MODE=FORCE  

### C-2.13) ORA-01403 Error in gllseq

> The Journal Import Log file shows the following errors:  
> 
> ORACLE error 1455 in fdsgsv  
> Cause: fdsgsv failed due to ORA-01455: converting column overflows integer datatype  
> The SQL statement being executed at the time of the error was:  
> SELECT FND_DOC_SEQ_4_S.NEXTVAL FROM SYS.DUAL  
> Error in: gllseq  
> ORA-01403: no data found
> 
>   
> The Sequence number has exceeded the limit of 9 digits.  
> After identifying the sequence with problems it must be disabled and a new sequence assigned in GL.  
> See  KB758690  for more information.

### C-2.14) ORA-01403 Error in gllsys

> The Journal Import Log file shows the following error:  
> 
> gllsys() 14-MAY-2003 15:50:05  
> Cannot read value for profile option UNIQUE:SEQ_NUMBERS in routine &ROUTINE...  
> Error in: gllsysFunction return status: 0  
> Function Err Message: failure to get sequential numbering profile option  
> Function warning number: -1  
> *****************************************************  
> sqlcaid: sqlabc: 0 sqlcode: 0 sqlerrml: 0  
> sqlerrmc:  
> ORA-1403: no data found
> 
>   
> The profile option Sequential Numbering is not correctly set.  
> Choose the 'Never Used' or 'Partially Used' values to import lines for this category.  
> If the 'Always Used' is chosen then all categories must have a valid sequence assignment.  
> See  KB749236  for more information.

### C-2.15) ORA-01403 Error in glpiil

> The Journal Import log file shows the following errors:  
> 
> SHRD0150: glpmii():  
> Could not find any data in GL_STORAGE_PARAMETERS  
> for object GL_INTERCO_BSV_INT/_U1.\par  
> glpiil ORA-01403: no data found
> 
>   
> This problem occurs on file glpmii.lpc version 115.3.  
> Install Patch:2078788 to update GL_STORAGE_PARAMETERS.  
>   

### C-2.16) ORA-01410 Error in gllcje

> The Journal Import Log file shows the following error:  
> 
> Error in: gllcje  
> Function return status: 0  
> Function Err Message: Fetching MAIN1 using descriptor ezlselda  
> Function warning number: -1sqlcaid: sqlabc: 0 sqlcode: -1410 sqlerrml: 25  
> sqlerrmc:  
> ORA-01410: invalid ROWID
> 
>   
> Execute just a few Journal Imports at a time.  
> The specified number of Sources / Group Ids to import must not exceed 20.  

### C-2.17) ORA-01455 Error in gllsys

> The Journal Import Log file shows the following error:  
> 
> Error in: gllsys  
> Function return status: 0  
> Function Err Message: sqlerror trapped at errexit  
> Function warning number: -1  
> *****************************************************  
> sqlcaid: sqlabc: 0 sqlcode: -1455 sqlerrml: 56  
> sqlerrmc:  
> ORA-1455: converting column overflows integer datatype
> 
>   
> Navigate to Setup-> System-> Control and verify the values for:  
> Number of Accounts in Memory  
> Number of Journal Lines to Process at Once  
> The values in those fields should not be excessive  
> See  [99779.1](https://support.oracle.com/rs?type=doc&id=99779.1 "99779.1")  for more information.

### C-2.18) ORA-01632

> The journal import Log file shows as error like the following:  
> 
> *****************************************************  
> sqlcaid: sqlabc: 0 sqlcode: -1632 sqlerrml: 66  
> sqlerrmc:  
> ORA-01632: max # extents (%) reached in index GL.[index_name]
> 
>   
> The DBA needs to increase the max extents of the index identified in the error line.  
> Then the Journal Import must be manually submitted for the same Source and specifying the Group Id.  
> See  [160038.1](https://support.oracle.com/rs?type=doc&id=160038.1 "160038.1")  and  KB722994  for more information.

### C-2.19) ORA-01652

> The Journal Import Log file shows an error like the following:  
> 
> ORA-01652 unable to extend temp segment by N in tablespace TABLESPACE
> 
>   
> An "unable to extend" error is raised when there is insufficient contiguous space available to extend the object. In this case, failed to allocate an extent for temp segment in tablespace.  
> The DBA must increase the size of the tablespace. See  [19047.1](https://support.oracle.com/rs?type=doc&id=19047.1 "19047.1")  for more information  
>   
> Having fixed the size problem the Journal Import must be manually submitted for the same Source and specific Group Id.  
> The Group Id needs to be entered manually because sometimes it is not available from the list of values.

### C-2.20) ORA-01653

> The Journal Import Log file shows the following error:  
> 
> ORA-01653 : unable to extend table [table_name]
> 
>   
> a) Increase the tablespace for the tables referenced in the error at the database level.  
> See  KB725565  for more information.  
>   
> b) when this error occurs the transactions are rolled-back, so you need to manually submit the Journal Import process for the same Source and Group_Id.

### C-2.21) ORA-01654

> The Journal Import Log file shows the following error:  
> 
> ORA-01654: unable to extend index [index_name] by 1280 in tablespace
> 
>   
> a) Identify the tablespace in question and add a datafile to it.  
>   
> b) After this error the transactions are rolled-back so you need to manually re-submit the Journal Import program for the same Source and Group_Id.

### C-2.22) ORA-03113 Error in gllcje

> The Journal Import Log file shows the following errors:  
> 
> Error in: gllcje  
> Function return status: 0  
> Function Err Message: Executing ins_prep using descriptor insbindda  
> Function warning number: -1  
> *****************************************************  
> sqlcaid: sqlabc: 0 sqlcode: -3113 sqlerrml: 48  
> sqlerrmc:  
> ORA-03113: end-of-file on communication channel  
> sqlerrp: sqlerrd: 0 1 0 0 0 538976288  
> sqlwarn: sqltext:  
> *****************************************************  
> SHRD0044: Process logging off database and exiting ...  
> ...  
> Program was terminated by signal 11
> 
>   
> Need to correct bad data loaded into the GL_INTERFACE table.  
> See  KB789536  for more information

### C-2.23) APP-00416 sfmmll cannot allocate memory

> The process log file shows the error message:  
> 
> APP-00416 sfmmll cannot allocate memory for buffer because system is out of memory
> 
>   
> Navigate to Setup > System > Controls and check the Number of Journal Lines to Process at Once.  
> Lower this value, to decrease the amount of memory being used at any one time by Journal Import.  
> See  [153412.1](https://support.oracle.com/rs?type=doc&id=153412.1 "153412.1")  for more information

### C-2.24) APP-FND-01388

> The process log file shows message:  
> 
> APP-FND-01388: Cannot read value for profile option GL_JI_IGNORE_CURRENCY_DATE in routine &ROUTINE.
> 
>   
> Mini-pack 11i.GL.F introduced the new feature GL Journal Import: Bypass Currency End Date, which requires a new profile option.  
> If you do not want to use this new feature then you do not need to do anything.  
> Otherwise create the profile option "Bypass Currency Date". This profile option is not seeded with the patch and must be manually created if you want to use this feature.  
> This profile option once created can be set at the site, application, responsibility and user levels.  
> See  [229708.1](https://support.oracle.com/rs?type=doc&id=229708.1 "229708.1")  for more information.

### C-2.25) LEZL0008: Found no interface records to process.

> Journal Import completes with Warning status.  
> The Log file shows the following message:  
> 
> LEZL0008: Found no interface records to process.
> 
>   
> 
> 1.  The lines are stuck in the GL_INTERFACE table due to an ORA error during Journal Imported or some interruption of the OS process. In this case please log a Service Request on My Oracle Support as this may require a datafix.  
>       
>     
> 2.  If the import source is 'AX Inventory', then probably some post-install scripts were missed.  
>     See documentation for more information.  
>       
>     
> 3.  This can be due to profile option 'Loop Monitoring' seting to YES. Import should work with loop monitoring option set to NO.  
>     See  KB707938  for more information.  
>       
>     
> 4.  If the 'All Group Ids' was chosen on the Import Journals form but all the lines in GL_INTERFACE have a NULL group_id they will not be found. The 'No Group Id' should be chosen instead.  
>     If the 'No Group Ids' was chosen on the Import Journals form but all the lines in GL_INTERFACE have a group_id they will not be found. The 'All Group Ids' or the 'Specific Group Id' should be chosen instead.  
>     See  KB722849  for more information.

### C-2.26) SQL-2112 Error in gllsys

> The Journal Import Log file shows the following error:  
> 
> Error in: gllsys.gllhid  
> Function Err Message: Failure to get a new je_header_id  
> SQL-02112: PCC:select into returns too many rows
> 
>   
> Probable cause is multiple rows existing in system.dual table.

### C-2.27) Terminated by Signal 11 or Signal 10

> The Journal Import Log file shows the following Error:  
> 
> Program was terminated by signal 11  
> or  
> Program was terminated by signal 10
> 
>   
> 1. Install patch with latest code for Journal Import.  
> A possible fix for this problem is available since Patch:3935957 (included on 11i.GL.K).  
> See  KB721737  for more information.  
>   
> 2. More than 20 selected source + group_id combinations selected for one single run may cause this problem. You must choose less combinations.  
> See  KB730322  for more information.  
>   
> 3. If the error occurs only for a huge number of lines for the same group_id then install Patch:2608405 (included on 11.5.9 or 11i.GL.H).

----------

### **D) Import Performance**

There may exist some different causes for a bad performance in Journal Import process.  
  
If you have a general poor performance in Journal Import then please follow the recommendations from  KB626741  How to Improve Journal Import Performance.  
  
If the performance problem only occurs for high volume batches then review  KB738781  GLLEZL: Problems Importing Very Large Journal Batches  
Specific patches effecting Journal Import Performance:

-   Patch:1455528: Multi-Table Journal Import
-   Patch:2608405: GLLEZL SIGNAL 11 When a GROUP_ID has a huge number of lines in GL_INTERFACE
-   Patch:2717598: The records with the STATUS 'PROCESSED' in GL_INTERFACE remain forever...
-   Patch:3087842: The records with the STATUS 'PROCESSED' in GL_INTERFACE remain
-   Patch:3535059: APPSPERF:GL: GLLEZL not using BIND variables

----------

### **E) Import Printing Errors**

### E-1) Execution Report doesn't print

> Journal Import concurrent requests ending in Warning do not print the Journal Import Execution Report.  
>   
> Install Patch:3512876 .  
>   
> This patch provides a new profile option Concurrent:Print on Warning (CONC_PRINT_WARNING). When set to Yes, if the request completes with a status for warning, it will still be printed.

### E-2) Only Report Title is printed

> Journal Import Execution Report is only printing the Report Title and no data is printed.  
>   
> This is probably an incorrect initialization string for the Printer Driver.

----------

### **F) Data issues on Imported Journals**

Usually the Journal Import program does not produce changes to the data coming from GL_INTERFACE, so eventual errors found in the imported Journals should first be searched in the source application or sub-ledger that populated the interface table.  
  
Expected changes are produced by Journal Import when:  
- the option to Create Summary Journals is used (lines are summarized by account)  
- the Import Descriptive Flexfields is set to No (no DFF are imported)  
- the Interface Data Transformer is being used (the changes are applied to the gl_interface table and then imported)

### F-1) Account - Default Values on NULL segments

> Journal import populates the default defined segment values into NULL segment values incorrectly coming from sub-ledgers.  
> The Journal Import Proces should fail in these conditions.  
>   
> This problem was fixed by Patch:4177985, which is superseeded by Patch:4371895.

### F-2) Account - Disabled segment values imported

> Journal Import has created journals to accounts having disabled segment values.  
>   
> This is the expected standard behavior.  
> If the code combination (CCID) already exists and is enabled, then the validation process stops there - segment values are not checked.  
> If the CCID does not already exist, then journal import will check at the segment value level and also validates against cross validation rules.  
>   
> See  [1071129.6](https://support.oracle.com/rs?type=doc&id=1071129.6 "1071129.6")  for more information

### F-3) Account - Security Rules are ignored

> Journal Import doesn't check for the Security Rules assigned to the responsibility.  
>   
> This is the standard behavior - Journal Import only checks the security rules if a new account code combination is to be created.  
> If the account code combination already exists the security rules are not verified and the account is accepted. However the restricted users will not be able to see the journal lines with the secured accounts.

### F-4) Amounts - Negative amounts imported

> Imported journal shows negative amounts.  
>   
> This is expected when the sub-ledger or feedersystem populates the interface table with negative amounts.  
> Journal Import will not change a negative Debit into a Credit nor a negative Credit into a Debit.

### F-5) Amounts - both Debit and Credit on the same line

> Some Imported Journals have both Debit and Credit amounts populated on the same line.  
>   
> This is not an error.  
> This is normal when the Journal Import is run on Summary mode and also for Consolidation journals.  
> See  KB711594  for more information.

> If need to derive separate lines for debit amounts and credit amounts for the same account code in a consolidation Journal see  [370467.1](https://support.oracle.com/rs?type=doc&id=370467.1 "370467.1")

### F-6) Amounts - converted amounts are zero

> Converted Amounts are zero even when a rate is created to correct an EC04 error (conversion rate is not provided) and Journal Import is resubmitted.  
>   
> This happens because after the error EC04, the converted amounts are populated with zero, and when the converted amounts are not blank then the conversion rate is not used.  
> To have the new conversion rate to take effect then the converted amounts must be updated to NULL before resubmitting Journal Import.

### F-7) Batches Merged by Journal Import

> Either different batches are merged into a single batch by Journal Import.  
> or  
> Journal Import automatically launched by the feeder system cannot find any lines.  
>   
> This happens when the Group_ID is not being used in the source batches.  
> If multiple batches are created using the same source and period, when the Journal Import process is submitted for one of them, it will pick all the lines with the same selection criteria and may merge lines if they do not have a group_id.  
> In this case, if the journal import program is automatically launch by the feeder system (sub-ledger), it may end with 'No Data Found' because the lines were already picked by a previous Journal Import process for the same Source.  
>   
> If a group_id is used in the source lines then Journal Import is able to distinguish the lines for different batches.  
>   
> Enabling the usage of group_id depends on the feeder system used to populate the GL_INTERFACE lines.  
> Please refer to the respective Users Guide.

### F-8) Currency - currency type changed to 'User'

> The Currency Conversion Type in Journal Header gets changed after Journal Import.  
> The conversion type populated in GL_INTERFACE table is ignored and replaced by the standard type 'User'.  
>   
> This is the standard behavior - when the Converted Amounts are also populated in GL_INTERFACE then the conversion type is changed to 'User'.

### F-9) GL_Interface_History issues

> Either data in GL_INTERFACE_HISTORY table is always growing. How can this be stopped?  
> or  
> How to get data populated into GL_INTERFACE_HISTORY?  
>   
> Journal Import creates rows in this table for successful runs.  
> Oracle General Ledger does not use the information stored in this table. This information is used for historical reference only.  
> Note: This may decrease your Journal Import performance and increase database used space.  
>   
> To control the way the data is populated into this table navigate to Setup/System/Control and enable or disable the Journal Import Data check box.  
>   
> The rows from this table can be deleted or truncated as it will not effect General Ledger.

### F-10) How is the imported journals Batch Name derived?

> The batch name uses the first 50 characters from REFERENCE1 in GL_INTERFACE (optional) followed by:  
> - Source  
> - Request ID  
> - Actual Flag  
> - Group ID  
>   
> In Consolidation journals, the profile option GL Consolidation: Preserve Journal Batching set to Yes will preserve up to 50 characters of the original batch name plus batch ID in the source set of books to the target set of books.

### F-11) How are the accounting Periods and Dates derived by Journal Import?

> Journal Import selects the period corresponding to the accounting_date populated in GL_INTERFACE.  
> Then the imported lines are grouped by period and the Journal Entry is created with the accountig_date of the last calendar day of the period.  
> The contents of the period_name column in the GL_INTERFACE table is ignored, therefore it is not possible to import for adjusting periods.  
> Journal Import groups lines with the same Period into the same journal, even if the lines have different Accounting Dates, for all sets of books except:  
> - the set of books is an Average Daily Balances set of books  
> - the profile option GL Journal Import: Separate Journals by Accounting Date is set to YES  
> In these cases it would put lines with different Accounting Dates into separate journals.  
>   
> Since 11i.GL.F the behavior has changed to allow Journal Import to import data into adjustment periods and also to import data that is to be reversed into adjustment periods.  
> For budgets the PERIOD_NAME column in the GL_INTERFACE table will now be able to hold both adjustment and non-adjustment periods.  
> For actual and encumbrance data the period that the data will be imported to will now be controlled by a combination of the ACCOUNTING_DATE and the PERIOD_NAME:- if a valid period name is specified and that period contains the accounting date then that period is used;- otherwise the non-adjusting period that contains the accounting date is used  
> The REFERENCE8 column in the GL_INTERFACE table will now be able to hold both adjusting and non-adjusting reversal periodsor reversal date for Average Balance data.  
> See documentation for more information.

### F-12) The imported journal lines description is always 'Journal Import Created'.

> When Journal Import runs in summary mode the description will always be 'Journal Import Created'.  
> When Journal Import runs in detail mode the description will only be 'Journal Import Created' if REFERENCE10 is null,and the subledger_doc_sequence_value is null on GL_INTERFACE.  
> You need to run Journal Import in detail to import the REFERENCE10 into the line description.

### F-13) How are imported lines ordered in a journal and how can this be controlled?

> Journal Import process does not follow the order of lines in gl_interface to create the lines within a journal. It follows the following order (ascending):  
> 
> 1.  Code_combination_id
> 2.  Entered_dr
> 3.  Entered_cr
> 4.  Accounted_dr
> 5.  Accounted_cr
> 6.  There is no way to change this.
> 7.  Populating the je_line_num column in the gl_interface table is useless as journal import will ignore this (it is a required null column)
> 
> The Accounting Date is not used for sorting the lines.  
> Journal Import groups lines with the same Period into the same journal, even if the lines have different Accounting Dates, for all sets of books except:  
> - the set of books is an Average Daily Balances set of books  
> - the profile option GL Journal Import: Separate Journals by Accounting Date is set to YES  
> In these cases it would put lines with different Accounting Dates into separate journals.

### F-14) How are the imported journals Names derived?

> The journal name uses the first 25 characters from REFERENCE4 in GL_INTERFACE followed by (when relevant):  
> 
> -   category name,
> -   currency code,
> -   encumbrance type id,
> -   budget version id,
> -   conversion type,
> -   conversion rate,
> -   conversion date,
> -   reference8
> 
> This journal name is used to determine and agregate the imported lines into each journal.  
>   
> In Consolidation journals, the profile option GL Consolidation: Preserve Journal Batching set to Yes will preserve up to 25 characters of the original journal name plus journal ID in the source set of books to the target set of books.

### F-15) Journal Entry not updateable

> The Enter Journals form doesn't allow to change/delete data from unposted Imported Journals.  
>   
> 1. Probably the Source of the journal is freezed (to protect the reconciliation between the 2 systems).  
> Navigate to the Journal Sources window and query up the Source.  
> On the right Uncheck the Freeze Journals column and Save.  
> After changes are made to the journal re-freeze the journal source.  
>   
>   
> 2. The journal Source is not Frozen but probably the journal have reserved Funds:  
> - if the Funds were reserved by the feeding subledger (Payables for example) then it is not possible to update the Journal.- if the Funds were reserved by General Ledger then navigate to Journals\Review Journal, click on More Actions button and Unreserve the funds.

### F-16) Missing Journal Lines

> Journal Import runs through to completion and the report and log do not show any errors but the created journal is incomplete - some lines are missing.  
>   
> The journal post will produce a report for lines posted to Suspense with no apparent reason.  
> If Suspense Posting is not allowed in the Set of Books screen then the posting fails with Error 6.  
>   
> This is caused by a rare database condition causing import to miss some journal lines.  
> To fix this, RDBMS Patch: 2124693 needs to be installed.  
> This problem does not occur on RDBMS versions certified with E-Business Suite.  
>   
> **ATTENTION**:  
> 
> > RDBMS versions 11.2.0.1, 11.2.0.2 and 11.2.0.3 may cause similar problems.  
> > Please review ALERT:  GL Journal Import Lines Impacted by 11.2.0.1 to 11.2.0.3 RDBMS Bugs - (Doc ID PALRT2504)

### F-17) Missing Journals imported from a sub-ledger

> The transactions were posted from the sub-ledger to GL but the corresponding GL Journals can't be found.  
> 
> 1.  Probably an error occurred during the Journal Import process, or was aborted or it hasn't even started. Check if the transactions are still in the interface table.  
>     Also look for errors in the Journal Import Execution Report and the Journal Import Log file of the process.
> 2.  Check if you have security rules assigned to the responsibility, which could prevent you from seeing the data.
> 3.  Check if you have the imported Source and Category defined in GL

### F-18) References - not being imported

> Reference columns REFERENCE1 to REFERENCE10 in GL_JE_LINES table are not populated on imported journal, in spite of having populated the GL_INTERFACE with the corresponding REFERENCE_21 to REFERENCE_30 values.  
>   
> 
> 1.  When the Journal Import is run in Summary mode the reference fields go to GL_IMPORT_REFERENCES instead of GL_JE_LINES.
> 2.  The Journal Source may not be allowing the references to be imported. Navigate to Setup/Journal/Sources and query the Source used . The Import Journal References flag should be checked.

### F-19) Tax fields not populated on Imported Journals

> The Tax fields in the Journal Entry screen are not populated by Journal Importeven when Value Added Tax has been actived in GL and the feeder system has correctly populated the GL_interface table.  
>   
> This is the expected behavior.  
> Tax is only available for journals with a source of Manual, i.e. journals entered directly in the Enter Journals form.  
> It is not available for any other type of journal.  
>   
> See  KB747325  for more information.

----------

### **G) Form GLXJIDEL: Delete Journal Import Data**

### G-1) Cannot delete ADI journals when logged with NLS language

> Batch uploaded from ADI using NLS language other than US, and with error on Journal Import cannot be deleted from this form when using the same language.  
>   
> However when using the form in US it is possible to select the source Spreadsheet and delete the batch in error.  
>   
> Delete the journal lines transfered from ADI using ADI with the same language used to upload the transactions.  
>   
> General Ledger Icon  
> Select Submit Process  
> Select Delete journal import data from the General Ledger Interface.

### G-2) The List of Values does not contains the desired data

> Unable to delete data from the Journal Import Correct screen.  
> Batch has a group_id associated but it does not show in the List of Values  
>   
> This happens when the batch was not yet submited to import.  
> This can be confirmed by the previous script: the request_id must not be null.  
>   
> The GLXJIDEL form only allows data be deleted from gl_interface if it is erroneous (if have an error status).  
> This prevents the deletion of correct data.  
>   
> The batch must be imported, and then, if still needed, delete the created journal before posting. After posting the batch cannot be deleted, only reversal is possible.

### G-3) Translation problems

> Errors in Translated form  
>   
> The known translation problems were fixed on GLXJIDEL.fmb file version 115.5.  
> Please search My Oracle Support for this form version and your language.

----------

### **H) During Delete Journal Import Source process**

### H-1) Data is not deleted from GL_INTERFACE

> Delete Journal Import Data program does not delete records from GL_INTERFACE table  
>   
> Install Patch:4495476.

----------

### **I) Form GLXJICOR: Correct Journal Import Data**

  
This form is used for correction of data populated in the GL_INTERFACE table lines that were rejected during a Journal Import run, therefore with an error status.  
The detected errors are listed in the Journal Execution Report automatically generated by the Journal Import execution.  
  
Please note that errors do not necessarily mean incorrect data, for instance the 'EP01: This date is not in any open or future enterable period.' may just require to open the corresponding period.  
  
Please select below the problem occurring in this form:

### I-1) Entered Account Code Combinations are not verified by the defined Secutity Rules

> This is the intended behavior.  
> This form only performs minimum validations and Security Rules is not one of them.  
> The Security Rules will apply, after the journal is imported, on the Enter Journals form.  
>   

### I-2) Error APP-00812 plus ORA-1722

> Getting error:  
> 
> > APP-00812 Cannot read value from field GLEZLNK_1.LAST_UPDATE_DATE  
> > ORA-01722: invalid number
> 
> when correcting data from a legacy system.  
>   
> This is caused by incorrect data populated in entered_cr and entered_dr columns in the GL_INTERFACE.  
> The bad data may be corrected using sql.  
>   

### I-3) Error FRM-40505 plus ORA-1722 or FRM-40734

> Getting errors:  
> 
> > FRM-40505: Oracle error - Unable to perform query  
> > ORA-01722: invalid number  
> > or  
> > FRM-40734: Internal Error: PL/SQL Error occurred.
> 
> when correcting data from a legacy system.  
>   
> This is caused by a value being populated in the REFERENCE3 column of GL_INTERFACE. As stated in the User Guide this column is reserved for subledgers.  
> The bad data may be corrected using sql.

### I-4) Error FRM-40654

> Getting error:  
> 
> > FRM-40654: Record has been updated. Re-query block to see change
> 
> when correcting data from a legacy system.  
>   
> This is caused by trailing spaces or control characters in some of the columns in GL_INTERFACE table.  
>   
> Remove the invalid characters with the script afchrchk.sql. This is included since 11i.ATG_PF.H RUP3.  
> If you have it not available then you can take it from Patch:685474. This is a 11.0.3 patch but the script also works on 11i (copy it to $FND_TOP/sql).  
> 
> -   Backup the gl_interface table before applying this script.
> -   Run this script in sqlplus against the apps account. Arguments are:
> -   Table name to check: GL_INTERFACE
> -   Column name to check: blank (for all)
> -   Check for control chars as well as trailing spaces: Y
> -   Automatically fix errors: Y
> 
> Full instructions can be found on patch readme file.  
>   
> However this script does not remove the double-byte trailing spaces. In case of using a double-byte character-set, the source program must trim the data before populating the gl_interface table with it.  
> See  KB710525  for more information

### I-5) Frozen journal Source allowing updates

> The Correct Journal Import form is allowing customers to modify failed journal import data for frozen journal Sources.  
>   
> This is the standard behavior on releases 10, 11.0 and 11.5.  
> This enhancement ( Bug:3872150) is available on GLXJICOR.fmb version 116.10.  
> Now frozen source data cannot be modified and a message 'Journal source is frozen' is shown in the status bar.

----------

###   
**J) On Interface Data Transformer**

The Interface Data Transformer is a user-friendly tool that facilitates the import of data from external feeder systems into Oracle General Ledger. It takes data from external feeder systems that have been loaded into the GL_INTERFACE table and transforms it into the proper format for import into Oracle General Ledger based on rules that you define.  
  
The Interface Data Transformer offers a variety of ways to transform data in the GL_INTERFACE table. You can use string functions to parse and concatenate substrings, reference lookup tables to convert one value into another, or call PL/SQL functions to perform sophisticated transformations. You can even define conditions to control when transformation rules are applied and validate the results of the transformation through value sets and lookup tables. This flexibility makes it easier for you to integrate non-Oracle systems into Oracle General Ledger.  
  
This enhancement was first delivered by controlled production release Patch:3061521 (11i.GCS.A) but only available in Release 11.5.10.  
  
See  KB783060  for more information about the setup of this new feature.  
  
## References

MOS document id: 330821.1