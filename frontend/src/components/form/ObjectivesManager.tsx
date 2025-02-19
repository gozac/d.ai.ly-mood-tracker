// src/components/ObjectivesManager.tsx
import React, { useState, useEffect } from 'react';
import { 
  fetchUserObjectives, 
  createObjective, 
  updateObjective, 
  deleteObjective 
} from '../../services/api';
import { Objective } from '../../types';

interface ObjectivesManagerProps {
  onObjectivesChange?: (objectives: Objective[]) => void;
}

const ObjectivesManager: React.FC<ObjectivesManagerProps> = ({ onObjectivesChange }) => {
  const [objectives, setObjectives] = useState<Objective[]>([]);
  const [newObjectiveText, setNewObjectiveText] = useState('');

  // Charger les objectifs au montage du composant
  useEffect(() => {
    const loadObjectives = async () => {
      const fetchedObjectives = await fetchUserObjectives();
      setObjectives(fetchedObjectives);
      onObjectivesChange?.(fetchedObjectives);
    };

    loadObjectives();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Ajouter un nouvel objectif
  const handleAddObjective = async () => {
    if (!newObjectiveText.trim()) return;

    try {
      const newObjective = await createObjective({
        title: newObjectiveText,
        isCompleted: false
      });

      const updatedObjectives = [...objectives, newObjective];
      setObjectives(updatedObjectives);
      setNewObjectiveText('');
      onObjectivesChange?.(updatedObjectives);
    } catch (error) {
      console.error('Erreur lors de l\'ajout de l\'objectif', error);
    }
  };

  // Mettre à jour le statut d'un objectif
  const handleToggleComplete = async (id: string) => {
    const objective = objectives.find(obj => obj.id === id);
    if (!objective) return;

    try {
      const updatedObjective = await updateObjective(id, {
        isCompleted: !objective.isCompleted
      });

      const updatedObjectives = objectives.map(obj => 
        obj.id === id ? updatedObjective : obj
      );

      setObjectives(updatedObjectives);
      onObjectivesChange?.(updatedObjectives);
    } catch (error) {
      console.error('Erreur lors de la mise à jour de l\'objectif', error);
    }
  };

  // Supprimer un objectif
  const handleDeleteObjective = async (id: string) => {
    try {
      await deleteObjective(id);
      const updatedObjectives = objectives.filter(obj => obj.id !== id);
      setObjectives(updatedObjectives);
      onObjectivesChange?.(updatedObjectives);
    } catch (error) {
      console.error('Erreur lors de la suppression de l\'objectif', error);
    }
  };

  return (
    <div className="objectives-manager">
      <h3>Mes Objectifs Actuels</h3>
      
      <div className="add-objective-container">
        <input 
          type="text"
          value={newObjectiveText}
          onChange={(e) => setNewObjectiveText(e.target.value)}
          placeholder="Nouvel objectif"
        />
        <button onClick={handleAddObjective}>Ajouter</button>
      </div>

      <ul className="objectives-list">
        {objectives.map(objective => (
          <li key={objective.id} className="objective-item">
            <input 
              type="checkbox"
              checked={objective.isCompleted}
              onChange={() => handleToggleComplete(objective.id)}
            />
            <span 
              style={{ 
                textDecoration: objective.isCompleted ? 'line-through' : 'none' 
              }}
            >
              {objective.title}
            </span>
            <button onClick={() => handleDeleteObjective(objective.id)}>
              Supprimer
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ObjectivesManager;