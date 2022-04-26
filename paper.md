---
title: 'Diameter distribution by Deconvolution (DdD): WebApp for cheap and fast determination of particle size distribution (PSD) of semiconductor nanoparticles from optical measurements'


tags:
  - Python
  - Plotly Dash
  - nanoparticles
  - particle size distribution
  - deconvolution
  - semiconductor nanoparticles



authors:
  - name: Daniel T. Suárez
    orcid: 0000-0003-0545-6333
    affiliation: 1
  - name: Sara A. Bilmes
    affiliation: "1, 2"
  - name: María Luz Martínez Ricci
    affiliation: 2
  - name: Diego Onna
    affiliation: 1
    
    
affiliations:
 - name: Departamento de Química Inorgánica, Analítica y Química Física, Facultad de Ciencias Exactas y Naturales, Universidad de Buenos Aires, Buenos Aires, Argentina
   index: 1
 - name: Instituto de Química Física de los Materiales, Medio Ambiente y Energía, (INQUIMAE) CONICET Universidad de Buenos Aires, Buenos Aires, Argentina
   index: 2

date: 26 April 2022
# bibliography: paper.bib

# Summary

Particles with a diameter below 500nm are generating an increasing interest due to their applications in industry and research. In particular, semiconductor nanoparticles (SNPs) have applications in several fields such as catalysis, energy harvesting, light emission, and sensors kovalenko2015prospects. These applications rely on their properties which are determined by SNPs size, then the size characterization is essential for these applications onna2022loading. A usual way to represent the size is the Particle Size Distribution (PSD - e.g., histogram of sizes), which typically can be obtained by using electron microscopies. These methods look directly at the sample with an electron beam and measure and count the particles, but they are expensive in terms of money and time. Therefore, alternative methods, such as optical methods for size determination, are interesting approaches to a faster and cheaper characterization.
In this work, we present a WebApp that processes absorbance measurements from a spectrophotometer to obtain the PSD. Applying deconvolution to an absorbance spectrum of the sample (using a database with different sizes’ absorbance spectra), the goal can be achieved with excellent accuracy onna2019diameter. The app lets you upload your data, calculate and view the PSD, and export the result.

# Statement of Need

This WebApp is aimed at people in research and development that frequently work with SNPs. Typically, a routine characterization consists in determining the size distribution of a new SNPs obtained sample. This task is frequently limited due to de access to advanced equipment.
Diameter distribution by Deconvolution (DdD) was created to assist anyone who has restricted access to expensive characterization techniques, making it possible to help researchers with a small budget for working in this field. It can also be useful for education purposes where advanced techniques are generally not available.
We believe that this graphical user interface is intuitive for everyone since it does not require the user to know any programming language or any of the analytical methods used in the WebApp.




# Acknowledgements

This work was supported by Universidad de Buenos Aires (UBACyT 20020190200245BA & 20020190100299BA). D. O., S. A. B. and M. L. M. R are members of CONICET. 
 

# References
