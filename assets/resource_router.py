"""
Civic Bridge Initiative - Resource Router
Core MILP optimization engine for municipal resource allocation.
"""

from pulp import *
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class Resource:
    id: str
    name: str
    capacity: float
    location: Tuple[float, float]
    resource_type: str


@dataclass
class Demand:
    zone_id: str
    resource_type: str
    predicted_demand: float
    confidence: float
    timestamp: datetime


@dataclass
class Route:
    vehicle_id: str
    stops: List[str]
    total_distance: float
    estimated_time: float
    load: float


class CivicRouter:
    """
    Mixed-Integer Linear Programming solver for civic resource routing.
    Optimizes allocation of shelters, food banks, and vehicle routes.
    """
    
    def __init__(self, config_path: str = "config/milp_config.json"):
        with open(config_path) as f:
            self.config = json.load(f)
        
        self.solver = PULP_CBC_CMD(
            timeLimit=self.config["solver"]["time_limit_seconds"],
            threads=self.config["solver"]["threads"],
            gapRel=self.config["solver"]["gap_tolerance"]
        )
    
    def optimize_allocation(
        self,
        resources: List[Resource],
        demands: List[Demand]
    ) -> Dict:
        """
        Solve resource allocation problem.
        Returns optimal allocation of resources to demand zones.
        """
        prob = LpProblem("Civic_Resource_Allocation", LpMinimize)
        
        # Decision variables
        alloc = LpVariable.dicts(
            "allocation",
            [(r.id, d.zone_id) for r in resources for d in demands],
            lowBound=0,
            cat='Continuous'
        )
        
        # Objective: minimize total unmet demand weighted by priority
        unmet = LpVariable.dicts(
            "unmet_demand",
            [d.zone_id for d in demands],
            lowBound=0,
            cat='Continuous'
        )
        
        # Primary objective: minimize unmet demand
        prob += lpSum(unmet[d.zone_id] for d in demands)
        
        # Constraints
        for d in demands:
            # Demand satisfaction: allocation + unmet = demand
            prob += (
                lpSum(alloc[(r.id, d.zone_id)] for r in resources) + unmet[d.zone_id] == d.predicted_demand,
                f"demand_{d.zone_id}"
            )
        
        for r in resources:
            # Capacity constraint
            prob += (
                lpSum(alloc[(r.id, d.zone_id)] for d in demands) <= r.capacity,
                f"capacity_{r.id}"
            )
        
        # Fairness constraint: minimum allocation ratio
        if self.config["constraints"]["fairness"]["enabled"]:
            min_ratio = self.config["constraints"]["fairness"]["minimum_allocation_ratio"]
            avg_demand = sum(d.predicted_demand for d in demands) / len(demands)
            
            for d in demands:
                prob += (
                    lpSum(alloc[(r.id, d.zone_id)] for r in resources) >= min_ratio * d.predicted_demand,
                    f"fairness_{d.zone_id}"
                )
        
        # Solve
        prob.solve(self.solver)
        
        # Extract solution
        solution = {
            "status": LpStatus[prob.status],
            "objective_value": value(prob.objective),
            "allocations": {},
            "unmet_demand": {},
            "timestamp": datetime.now().isoformat()
        }
        
        for d in demands:
            solution["allocations"][d.zone_id] = {
                r.id: value(alloc[(r.id, d.zone_id)]) 
                for r in resources
            }
            solution["unmet_demand"][d.zone_id] = value(unmet[d.zone_id])
        
        return solution
    
    def optimize_routes(
        self,
        vehicles: List[Dict],
        stops: List[Dict],
        depot_location: Tuple[float, float]
    ) -> List[Route]:
        """
        Solve vehicle routing problem for resource delivery.
        Returns optimized routes for each vehicle.
        """
        prob = LpProblem("Civic_Vehicle_Routing", LpMinimize)
        
        # Simplified VRP - in production use OR-Tools
        n_vehicles = len(vehicles)
        n_stops = len(stops)
        
        # Decision variables: x[v][i][j] = 1 if vehicle v goes from i to j
        x = LpVariable.dicts(
            "route",
            [(v, i, j) for v in range(n_vehicles) 
                      for i in range(n_stops + 1) 
                      for j in range(n_stops + 1)],
            cat='Binary'
        )
        
        # Objective: minimize total distance
        distances = self._compute_distances(depot_location, stops)
        prob += lpSum(
            distances[i][j] * x[(v, i, j)]
            for v in range(n_vehicles)
            for i in range(n_stops + 1)
            for j in range(n_stops + 1)
        )
        
        # Constraints: each stop visited exactly once
        for j in range(1, n_stops + 1):
            prob += (
                lpSum(x[(v, i, j)] for v in range(n_vehicles) 
                                   for i in range(n_stops + 1)) == 1,
                f"visit_{j}"
            )
        
        # Solve
        prob.solve(self.solver)
        
        # Extract routes
        routes = []
        for v in range(n_vehicles):
            route_stops = []
            for i in range(n_stops + 1):
                for j in range(n_stops + 1):
                    if value(x[(v, i, j)]) == 1:
                        route_stops.append(j)
            
            if route_stops:
                routes.append(Route(
                    vehicle_id=vehicles[v]["id"],
                    stops=[stops[s-1]["id"] for s in route_stops if s > 0],
                    total_distance=0,  # Computed from solution
                    estimated_time=0,
                    load=0
                ))
        
        return routes
    
    def _compute_distances(
        self, 
        depot: Tuple[float, float], 
        stops: List[Dict]
    ) -> List[List[float]]:
        """Compute distance matrix including depot."""
        all_points = [depot] + [(s["lat"], s["lon"]) for s in stops]
        n = len(all_points)
        dist = [[0.0] * n for _ in range(n)]
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    # Haversine approximation
                    lat1, lon1 = all_points[i]
                    lat2, lon2 = all_points[j]
                    dist[i][j] = ((lat2-lat1)**2 + (lon2-lon1)**2) ** 0.5 * 111  # km
        
        return dist


def main():
    """Example usage with sample data."""
    router = CivicRouter()
    
    # Sample resources
    resources = [
        Resource("shelter_1", "Main Shelter", 150, (40.7128, -74.0060), "shelter"),
        Resource("shelter_2", "Overflow Shelter", 75, (40.7580, -73.9855), "shelter"),
        Resource("food_1", "Central Food Bank", 5000, (40.7484, -73.9857), "food"),
    ]
    
    # Sample demand forecast
    demands = [
        Demand("zone_1", "shelter", 120, 0.9, datetime.now()),
        Demand("zone_2", "shelter", 80, 0.85, datetime.now()),
        Demand("zone_3", "food", 3000, 0.95, datetime.now()),
    ]
    
    # Solve
    solution = router.optimize_allocation(resources, demands)
    print(json.dumps(solution, indent=2))


if __name__ == "__main__":
    main()
