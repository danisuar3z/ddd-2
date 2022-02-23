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

date: 10 February 2022
# bibliography: paper.bib
---

# Summary

Particles with a diameter below 500 nm are generating an increasing interest for their applications in industry and research. In particular, semiconductor nanoparticles (SNPs) have applications in fields like catalysis, energy harvesting, light emission and sensors (10.1021/nn506223h). These applications rely on their properties which are strongly determined by SNPs size, then size characterization is essential for these applications. An usual way to represent the size is the Particle Size Distribution (PSD - e.g., histogram of sizes), that typically can be resolved using electron microscopes. This method looks directly at the sample with an electron beam and measures and counts the particles, but it is expensive in terms of money and time. Therefore, alternative methods, such as optical size determination, are interesting approaches to a faster and cheaper characterization.
Here we present a WebApp that processes absorbance measurements from a spectrophotometer to obtain the PSD. Applying deconvolution to an absorbance spectrum of the sample (using a database with different sizes’ absorbance spectra), the goal can be achieved with very good approximation. The app lets you upload your data, calculate and view the PSD, and export the result.

# Statement of Need

This WebApp is aimed at people in research and development that frequently works with SNPs. As of today, most of the routine characterization is centered in size determination and is strongly limited for the access to advanced equipment.
Diameter distribution by Deconvolution (DdD) was created to assist anyone who has few access to expensive characterization techniques, making it possible to help researchers with a small budget for working in this field.
We believe that this graphical user interface is intuitive for everyone, besides that it does not require the user to know any programming language or the analytical methods used in the WebApp.

# Acknowledgements

# References
