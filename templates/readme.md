Some more sofisticated examples of how the toolkit can be used. To make efficient use of the toolkit one must seperate *analysis* and *visualization* from one another. 

The *analysis* uses two programming paradigmas:

1. Data related parameters should not be set within python scripts, but within yaml files. 
  This makes the templates much easier to resuse for new projects.
2. Each intermediate result should be saved as a *json* file before futher use.
  This automaticaly forces you to seperate visualization and analysis. Further it helps with the later reuse of the data, as the intermediate *json* objects can just be imported and reused without any prior knowlege of there history. During data exploration it is a bit annoying as it adds an extra layer of complexity, but it is very worth wile doing so.