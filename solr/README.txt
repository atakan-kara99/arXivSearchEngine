To reconstruct the index, you have to 
copy/paste the config directory into your 
solr core config directory.

Go to your solr dir -> server -> solr -> <ur_core_name> 
And paste the config dir here..

You can easily build the index.



#######################
#    R E I N D E X    #
#######################

First of all, you need to update your 'managed-schema' at your 
core's directory.
For help, just look above.


To reindex you have to:
 -> ./solr restart or
 -> ./solr start (if it isn't already running)

(2)
We need to delete our index data and our documents:
Go to 
http://localhost:8983/solr/#/inf_ret/

-> Documents (left hand side sidebar menu under your core name 'inf_ret')
-> Select as 'Document Type' 'XML'
-> for 'Document(s)' just insert: <delete><query>*:*</query></delete>
-> Submit Document

Now you have deleted your index.

(3) Use the ./post command or post.jar to index it again.
Now you can search in your index like before.