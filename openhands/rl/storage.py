"""
Trajectory storage for reinforcement learning in OpenHands.

This module implements storage backends for saving and retrieving
reinforcement learning trajectories.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import json
import os
import uuid
import datetime


class ITrajectoryStorage(ABC):
    """Interface for trajectory storage backends."""
    
    @abstractmethod
    def save_trajectories(
        self,
        env_name: str,
        task_ids: List[int],
        trajectories: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Save trajectories to storage.
        
        Args:
            env_name: Name of the environment
            task_ids: List of task IDs
            trajectories: List of trajectory dictionaries
            metadata: Additional metadata
            
        Returns:
            List of trajectory IDs
        """
        pass
    
    @abstractmethod
    def get_trajectory(self, trajectory_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a trajectory by ID.
        
        Args:
            trajectory_id: ID of the trajectory
            
        Returns:
            Trajectory dictionary or None if not found
        """
        pass
    
    @abstractmethod
    def get_trajectories(
        self,
        env_name: Optional[str] = None,
        task_id: Optional[int] = None,
        limit: int = 100,
        offset: int = 0,
        sort_by: str = "timestamp",
        sort_order: str = "desc"
    ) -> List[Dict[str, Any]]:
        """
        Retrieve trajectories with filtering and pagination.
        
        Args:
            env_name: Filter by environment name
            task_id: Filter by task ID
            limit: Maximum number of trajectories to return
            offset: Offset for pagination
            sort_by: Field to sort by
            sort_order: Sort order ("asc" or "desc")
            
        Returns:
            List of trajectory dictionaries
        """
        pass


class FileTrajectoryStorage(ITrajectoryStorage):
    """File-based trajectory storage."""
    
    def __init__(self, storage_dir: str = None):
        """
        Initialize file-based trajectory storage.
        
        Args:
            storage_dir: Directory to store trajectory files
        """
        self.storage_dir = storage_dir or os.path.join(
            os.path.expanduser("~"),
            ".openhands",
            "rl_trajectories"
        )
        os.makedirs(self.storage_dir, exist_ok=True)
    
    def save_trajectories(
        self,
        env_name: str,
        task_ids: List[int],
        trajectories: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Save trajectories to files.
        
        Args:
            env_name: Name of the environment
            task_ids: List of task IDs
            trajectories: List of trajectory dictionaries
            metadata: Additional metadata
            
        Returns:
            List of trajectory IDs
        """
        # Create environment directory
        env_dir = os.path.join(self.storage_dir, env_name)
        os.makedirs(env_dir, exist_ok=True)
        
        # Generate IDs and save trajectories
        trajectory_ids = []
        
        for i, (task_id, trajectory) in enumerate(zip(task_ids, trajectories)):
            # Generate unique ID
            trajectory_id = str(uuid.uuid4())
            trajectory_ids.append(trajectory_id)
            
            # Add metadata
            timestamp = datetime.datetime.now().isoformat()
            trajectory_with_meta = {
                "id": trajectory_id,
                "env_name": env_name,
                "task_id": task_id,
                "timestamp": timestamp,
                "metadata": metadata or {},
                "trajectory": trajectory
            }
            
            # Save to file
            file_path = os.path.join(env_dir, f"{trajectory_id}.json")
            with open(file_path, "w") as f:
                json.dump(trajectory_with_meta, f, indent=2)
        
        return trajectory_ids
    
    def get_trajectory(self, trajectory_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a trajectory by ID.
        
        Args:
            trajectory_id: ID of the trajectory
            
        Returns:
            Trajectory dictionary or None if not found
        """
        # Search for the trajectory file
        for env_name in os.listdir(self.storage_dir):
            env_dir = os.path.join(self.storage_dir, env_name)
            if not os.path.isdir(env_dir):
                continue
            
            file_path = os.path.join(env_dir, f"{trajectory_id}.json")
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    return json.load(f)
        
        return None
    
    def get_trajectories(
        self,
        env_name: Optional[str] = None,
        task_id: Optional[int] = None,
        limit: int = 100,
        offset: int = 0,
        sort_by: str = "timestamp",
        sort_order: str = "desc"
    ) -> List[Dict[str, Any]]:
        """
        Retrieve trajectories with filtering and pagination.
        
        Args:
            env_name: Filter by environment name
            task_id: Filter by task ID
            limit: Maximum number of trajectories to return
            offset: Offset for pagination
            sort_by: Field to sort by
            sort_order: Sort order ("asc" or "desc")
            
        Returns:
            List of trajectory dictionaries
        """
        trajectories = []
        
        # Determine which environments to search
        env_dirs = []
        if env_name:
            env_dir = os.path.join(self.storage_dir, env_name)
            if os.path.isdir(env_dir):
                env_dirs.append(env_dir)
        else:
            for name in os.listdir(self.storage_dir):
                env_dir = os.path.join(self.storage_dir, name)
                if os.path.isdir(env_dir):
                    env_dirs.append(env_dir)
        
        # Collect trajectories
        for env_dir in env_dirs:
            for filename in os.listdir(env_dir):
                if not filename.endswith(".json"):
                    continue
                
                file_path = os.path.join(env_dir, filename)
                with open(file_path, "r") as f:
                    trajectory = json.load(f)
                
                # Apply task_id filter if specified
                if task_id is not None and trajectory.get("task_id") != task_id:
                    continue
                
                trajectories.append(trajectory)
        
        # Sort trajectories
        reverse = sort_order.lower() == "desc"
        trajectories.sort(key=lambda x: x.get(sort_by, ""), reverse=reverse)
        
        # Apply pagination
        return trajectories[offset:offset + limit]


class MongoDBTrajectoryStorage(ITrajectoryStorage):
    """MongoDB-based trajectory storage."""
    
    def __init__(
        self,
        connection_string: str = "mongodb://localhost:27017/",
        database_name: str = "openhands_rl"
    ):
        """
        Initialize MongoDB-based trajectory storage.
        
        Args:
            connection_string: MongoDB connection string
            database_name: Name of the database
        """
        try:
            from pymongo import MongoClient
            
            self.client = MongoClient(connection_string)
            self.db = self.client[database_name]
            self.collection = self.db["trajectories"]
            
            # Create indexes
            self.collection.create_index("env_name")
            self.collection.create_index("task_id")
            self.collection.create_index("timestamp")
        except ImportError:
            raise ImportError(
                "MongoDB storage requires pymongo. "
                "Install it with: pip install pymongo"
            )
    
    def save_trajectories(
        self,
        env_name: str,
        task_ids: List[int],
        trajectories: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Save trajectories to MongoDB.
        
        Args:
            env_name: Name of the environment
            task_ids: List of task IDs
            trajectories: List of trajectory dictionaries
            metadata: Additional metadata
            
        Returns:
            List of trajectory IDs
        """
        # Generate IDs and prepare documents
        trajectory_ids = []
        documents = []
        
        for i, (task_id, trajectory) in enumerate(zip(task_ids, trajectories)):
            # Generate unique ID
            trajectory_id = str(uuid.uuid4())
            trajectory_ids.append(trajectory_id)
            
            # Create document
            document = {
                "_id": trajectory_id,
                "id": trajectory_id,
                "env_name": env_name,
                "task_id": task_id,
                "timestamp": datetime.datetime.now(),
                "metadata": metadata or {},
                "trajectory": trajectory
            }
            
            documents.append(document)
        
        # Insert documents
        if documents:
            self.collection.insert_many(documents)
        
        return trajectory_ids
    
    def get_trajectory(self, trajectory_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a trajectory by ID.
        
        Args:
            trajectory_id: ID of the trajectory
            
        Returns:
            Trajectory dictionary or None if not found
        """
        document = self.collection.find_one({"_id": trajectory_id})
        if document:
            # Convert ObjectId to string for JSON serialization
            document["_id"] = str(document["_id"])
            return document
        
        return None
    
    def get_trajectories(
        self,
        env_name: Optional[str] = None,
        task_id: Optional[int] = None,
        limit: int = 100,
        offset: int = 0,
        sort_by: str = "timestamp",
        sort_order: str = "desc"
    ) -> List[Dict[str, Any]]:
        """
        Retrieve trajectories with filtering and pagination.
        
        Args:
            env_name: Filter by environment name
            task_id: Filter by task ID
            limit: Maximum number of trajectories to return
            offset: Offset for pagination
            sort_by: Field to sort by
            sort_order: Sort order ("asc" or "desc")
            
        Returns:
            List of trajectory dictionaries
        """
        # Build query
        query = {}
        if env_name:
            query["env_name"] = env_name
        if task_id is not None:
            query["task_id"] = task_id
        
        # Determine sort direction
        sort_direction = -1 if sort_order.lower() == "desc" else 1
        
        # Execute query
        cursor = self.collection.find(query)
        cursor = cursor.sort(sort_by, sort_direction)
        cursor = cursor.skip(offset).limit(limit)
        
        # Convert documents
        trajectories = []
        for document in cursor:
            # Convert ObjectId to string for JSON serialization
            document["_id"] = str(document["_id"])
            trajectories.append(document)
        
        return trajectories