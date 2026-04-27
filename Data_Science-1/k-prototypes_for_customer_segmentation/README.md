<p align="center">
  <img width="465" height="310" src="https://competitions-app.datacamp.com/1.8.1/medical-device-customers/medical-device-customers.jpg">
</p>

# Notebook created for the Datacamp competition on : [Datacamp Competition](https://app.datacamp.com/workspace/w/d4f9e3b2-d586-4b40-b490-44cc9af3c53b)


<p align="center">
  <img width="460" height="460" src="https://github.com/rafaeldjsm/Data_Science/blob/master/k-prototypes_for_customer_segmentation/venn_join.png">
</p>


----------
# [Github Notebook ](https://github.com/rafaeldjsm/Data_Science/blob/master/k-prototypes_for_customer_segmentation/k-prototypes_for_customer_segmentation.ipynb) 


# Can you find a better way to segment your customers?

## 📖 Background
You work for a medical device manufacturer in Switzerland. Your company manufactures orthopedic devices and sells them worldwide. The company sells directly to individual doctors who use them on rehabilitation and physical therapy patients.

Historically, the sales and customer support departments have grouped doctors by geography. However, the region is not a good predictor of the number of purchases a doctor will make or their support needs.

Your team wants to use a data-centric approach to segmenting doctors to improve marketing, customer service, and product planning.

**Sumary**:

1. Imports\
	1.1. Exploratory Data Analysis
2. How many doctors are there in each region? What is the average number of purchases per region?
3. Can you find a relationship between purchases and complaints?
4. Define new doctor segments that help the company improve marketing efforts and customer service.
5. Identify which features impact the new segmentation strategy the most.

**This notebook aims to analyze the content of the customer database, indicating the main metrics that can be effective for the best marketing targeting. Based on this analysis, I develop a model that allows the clustering of doctors according to their intention to execute purchase orders, as well as their level of satisfaction, complaints and reworks.**

As we have many categorical variables, we will use the k-prototypes method.<br>
One of the conventional clustering methods commonly used in clustering techniques and efficiently used for large data is the K-Means algorithm. However, its method is not good and suitable for data that contains categorical variables. This problem happens when the cost function in K-Means is calculated using the Euclidian distance that is only suitable for numerical data. While K-Mode is only suitable for categorical data only, not mixed data types.

k-modes is used for clustering categorical variables. It defines clusters based on the number of matching categories between data points. It defines clusters based on the number of matching categories between the data points and the distances/inertias/cost function c are calculated by dissimilarity.

Facing these problems, Huang proposed an algorithm called K-Prototype which is created in order to handle clustering algorithms with the mixed data types (numerical and categorical variables). K-Prototype is a clustering method based on partitioning. Its algorithm is an improvement of the K-Means and K-Mode clustering algorithm to handle clustering with the mixed data types.

References:<br>
[The K-modes algorithm for clustering](https://github.com/nicodv/kmodes)<br>
[HUANG97] Huang, Z.: Clustering large data sets with mixed numeric and
   categorical values, Proceedings of the First Pacific Asia Knowledge
   Discovery and Data Mining Conference, Singapore, pp. 21-34, 1997.<br>

[HUANG98] Huang, Z.: Extensions to the k-modes algorithm for clustering
   large data sets with categorical values, Data Mining and Knowledge
   Discovery 2(3), pp. 283-304, 1998.<br>

[CAO09] Cao, F., Liang, J, Bai, L.: A new initialization method for
   categorical data clustering, Expert Systems with Applications 36(7),
   pp. 10223-10228., 2009.

