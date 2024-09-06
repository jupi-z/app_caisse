-- Table Utilisateur
CREATE TABLE Utilisateur (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    prenom VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    mot_de_passe VARCHAR(255) NOT NULL
);

-- Table Étudiant
CREATE TABLE Etudiant (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    prenom VARCHAR(255) NOT NULL,
    matricule VARCHAR(255) NOT NULL UNIQUE,
    niveau VARCHAR(255) NOT NULL,
    filiere VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    telephone VARCHAR(255) NOT NULL
);

-- Table Frais
CREATE TABLE Frais (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    montant DECIMAL(10, 2) NOT NULL,
    date_echeance DATE NOT NULL,
    description TEXT
);

-- Table Paiement
CREATE TABLE Paiement (
    id INT AUTO_INCREMENT PRIMARY KEY,
    etudiant_id INT NOT NULL,
    frais_id INT NOT NULL,
    montant DECIMAL(10, 2) NOT NULL,
    date_paiement DATETIME NOT NULL,
    mode_paiement VARCHAR(255) NOT NULL,
    reference_paiement VARCHAR(255) NOT NULL,
    utilisateur_id INT NOT NULL,
    FOREIGN KEY (etudiant_id) REFERENCES Etudiant(id),
    FOREIGN KEY (frais_id) REFERENCES Frais(id),
    FOREIGN KEY (utilisateur_id) REFERENCES Utilisateur(id)
);