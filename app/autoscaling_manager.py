"""
Auto-Scaling Configuration for DocPro Fleet Management System
Handles dynamic scaling policies, metrics collection, and scaling thresholds
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum
import json
import logging
from datetime import datetime, timedelta


logger = logging.getLogger(__name__)


class ScalingMetric(Enum):
    """Types of metrics used for scaling decisions"""
    CPU = "cpu"
    MEMORY = "memory"
    REQUEST_RATE = "request_rate"
    RESPONSE_TIME = "response_time"
    QUEUE_DEPTH = "queue_depth"
    ACTIVE_CONNECTIONS = "active_connections"


class ScalingTrigger(Enum):
    """Trigger types for scaling events"""
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    SCALE_MAINTAIN = "maintain"


@dataclass
class ScalingThreshold:
    """Define when scaling should trigger"""
    metric: ScalingMetric
    upper_bound: float  # Scale up when exceeded
    lower_bound: float  # Scale down when below
    evaluation_periods: int = 3  # Periods to evaluate before scaling
    cooldown_seconds: int = 60  # Wait before next scaling action


@dataclass
class ScalingPolicy:
    """Policy that defines how to scale"""
    name: str
    triggers: List[ScalingThreshold]
    scale_up_increment: int  # How many pods to add
    scale_down_decrement: int  # How many pods to remove
    max_replicas: int
    min_replicas: int
    enabled: bool = True


@dataclass
class ScalingMetricsSnapshot:
    """Current state of scaling metrics"""
    timestamp: datetime
    cpu_utilization: float  # Percentage
    memory_utilization: float  # Percentage
    request_rate: float  # Req/sec
    average_response_time: float  # MS
    queue_depth: int  # Number of pending tasks
    active_connections: int
    current_replicas: int


class ScalingPolicies:
    """Pre-defined scaling policies for different workload types"""
    
    # Aggressive scaling for bursty workloads (file conversions)
    AGGRESSIVE = ScalingPolicy(
        name="aggressive",
        triggers=[
            ScalingThreshold(
                metric=ScalingMetric.CPU,
                upper_bound=60.0,
                lower_bound=30.0,
                evaluation_periods=2,
                cooldown_seconds=30
            ),
            ScalingThreshold(
                metric=ScalingMetric.REQUEST_RATE,
                upper_bound=500,  # req/sec
                lower_bound=100,
                evaluation_periods=2,
                cooldown_seconds=30
            ),
        ],
        scale_up_increment=4,
        scale_down_decrement=2,
        max_replicas=20,
        min_replicas=3
    )
    
    # Balanced scaling (default)
    BALANCED = ScalingPolicy(
        name="balanced",
        triggers=[
            ScalingThreshold(
                metric=ScalingMetric.CPU,
                upper_bound=70.0,
                lower_bound=40.0,
                evaluation_periods=3,
                cooldown_seconds=60
            ),
            ScalingThreshold(
                metric=ScalingMetric.MEMORY,
                upper_bound=75.0,
                lower_bound=45.0,
                evaluation_periods=3,
                cooldown_seconds=60
            ),
            ScalingThreshold(
                metric=ScalingMetric.REQUEST_RATE,
                upper_bound=1000,  # req/sec
                lower_bound=200,
                evaluation_periods=3,
                cooldown_seconds=60
            ),
        ],
        scale_up_increment=2,
        scale_down_decrement=1,
        max_replicas=15,
        min_replicas=3
    )
    
    # Conservative scaling (cost optimization)
    CONSERVATIVE = ScalingPolicy(
        name="conservative",
        triggers=[
            ScalingThreshold(
                metric=ScalingMetric.CPU,
                upper_bound=80.0,
                lower_bound=50.0,
                evaluation_periods=5,
                cooldown_seconds=120
            ),
            ScalingThreshold(
                metric=ScalingMetric.MEMORY,
                upper_bound=85.0,
                lower_bound=55.0,
                evaluation_periods=5,
                cooldown_seconds=120
            ),
        ],
        scale_up_increment=1,
        scale_down_decrement=1,
        max_replicas=10,
        min_replicas=2
    )


@dataclass
class ScalingEvent:
    """Record of a scaling action"""
    timestamp: datetime
    trigger_metric: ScalingMetric
    metric_value: float
    threshold: float
    action: ScalingTrigger
    replicas_before: int
    replicas_after: int
    policy_name: str
    reason: str


class AutoScalingManager:
    """Manages auto-scaling decisions and tracks scaling events"""
    
    def __init__(self, policy: ScalingPolicy = None):
        self.policy = policy or ScalingPolicies.BALANCED
        self.scaling_events: List[ScalingEvent] = []
        self.metric_history: Dict[ScalingMetric, List[float]] = {
            metric: [] for metric in ScalingMetric
        }
        self.last_scaling_time: Optional[datetime] = None
        self.current_replicas = self.policy.min_replicas
    
    def evaluate_metrics(self, snapshot: ScalingMetricsSnapshot) -> ScalingTrigger:
        """
        Evaluate current metrics against policy thresholds
        Returns: ScalingTrigger indicating scaling action
        """
        self.current_replicas = snapshot.current_replicas
        
        # Track metric history
        self.metric_history[ScalingMetric.CPU].append(snapshot.cpu_utilization)
        self.metric_history[ScalingMetric.MEMORY].append(snapshot.memory_utilization)
        self.metric_history[ScalingMetric.REQUEST_RATE].append(snapshot.request_rate)
        self.metric_history[ScalingMetric.RESPONSE_TIME].append(snapshot.average_response_time)
        self.metric_history[ScalingMetric.QUEUE_DEPTH].append(snapshot.queue_depth)
        self.metric_history[ScalingMetric.ACTIVE_CONNECTIONS].append(snapshot.active_connections)
        
        # Keep only last 10 samples per metric
        for metric in self.metric_history:
            if len(self.metric_history[metric]) > 10:
                self.metric_history[metric].pop(0)
        
        # Check if in cooldown period
        if self.last_scaling_time:
            time_since_last = (datetime.now() - self.last_scaling_time).total_seconds()
            if time_since_last < self.policy.triggers[0].cooldown_seconds:
                return ScalingTrigger.SCALE_MAINTAIN
        
        # Evaluate each trigger
        scale_up_count = 0
        scale_down_count = 0
        
        for trigger in self.policy.triggers:
            avg_value = self._get_average_metric(trigger.metric, trigger.evaluation_periods)
            
            if avg_value > trigger.upper_bound:
                scale_up_count += 1
            elif avg_value < trigger.lower_bound:
                scale_down_count += 1
        
        # Make decision based on evaluation
        if scale_up_count > 0:
            return ScalingTrigger.SCALE_UP
        elif scale_down_count > 0:
            return ScalingTrigger.SCALE_DOWN
        else:
            return ScalingTrigger.SCALE_MAINTAIN
    
    def _get_average_metric(self, metric: ScalingMetric, periods: int) -> float:
        """Get average value for metric over last N periods"""
        history = self.metric_history.get(metric, [])
        if not history:
            return 0.0
        
        sample_size = min(periods, len(history))
        return sum(history[-sample_size:]) / sample_size if sample_size > 0 else 0.0
    
    def calculate_replicas(self, trigger: ScalingTrigger) -> int:
        """Calculate target replica count based on trigger"""
        if trigger == ScalingTrigger.SCALE_UP:
            target = self.current_replicas + self.policy.scale_up_increment
        elif trigger == ScalingTrigger.SCALE_DOWN:
            target = max(self.policy.min_replicas, 
                        self.current_replicas - self.policy.scale_down_decrement)
        else:
            return self.current_replicas
        
        # Enforce min/max bounds
        return max(self.policy.min_replicas, 
                  min(self.policy.max_replicas, target))
    
    def record_scaling_event(self, snapshot: ScalingMetricsSnapshot, 
                            trigger: ScalingTrigger, new_replicas: int,
                            metric: ScalingMetric, metric_value: float,
                            reason: str):
        """Record a scaling event for audit trail"""
        trigger_threshold = None
        for t in self.policy.triggers:
            if t.metric == metric:
                trigger_threshold = t.upper_bound if trigger == ScalingTrigger.SCALE_UP else t.lower_bound
                break
        
        event = ScalingEvent(
            timestamp=datetime.now(),
            trigger_metric=metric,
            metric_value=metric_value,
            threshold=trigger_threshold or 0.0,
            action=trigger,
            replicas_before=snapshot.current_replicas,
            replicas_after=new_replicas,
            policy_name=self.policy.name,
            reason=reason
        )
        
        self.scaling_events.append(event)
        self.last_scaling_time = datetime.now()
        
        logger.info(f"Scaling event: {event.action.value} - "
                   f"{event.replicas_before} -> {event.replicas_after} replicas "
                   f"(Reason: {reason})")
    
    def get_scaling_history(self, hours: int = 24) -> List[ScalingEvent]:
        """Get scaling events from last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [e for e in self.scaling_events if e.timestamp >= cutoff_time]
    
    def get_metrics_summary(self) -> Dict:
        """Get summary of recent metrics"""
        return {
            "timestamp": datetime.now().isoformat(),
            "policy": self.policy.name,
            "current_replicas": self.current_replicas,
            "min_replicas": self.policy.min_replicas,
            "max_replicas": self.policy.max_replicas,
            "cpu_avg": self._get_average_metric(ScalingMetric.CPU, 5),
            "memory_avg": self._get_average_metric(ScalingMetric.MEMORY, 5),
            "request_rate_avg": self._get_average_metric(ScalingMetric.REQUEST_RATE, 5),
            "recent_events": len(self.get_scaling_history(hours=1))
        }


class MetricsCollector:
    """Collects metrics from Flask app for scaling decisions"""
    
    def __init__(self, app=None):
        self.app = app
        self._request_count = 0
        self._request_times = []
        self._active_connections = 0
        self._cpu_readings = []
        self._memory_readings = []
        self.start_time = datetime.now()
    
    def collect_metrics(self) -> ScalingMetricsSnapshot:
        """Collect current metrics snapshot"""
        import psutil
        import os
        
        # Get process metrics
        process = psutil.Process(os.getpid())
        cpu_percent = process.cpu_percent(interval=0.1)
        memory_info = process.memory_info()
        total_memory = psutil.virtual_memory().total
        memory_percent = (memory_info.rss / total_memory) * 100
        
        # Store readings for trend analysis
        self._cpu_readings.append(cpu_percent)
        self._memory_readings.append(memory_percent)
        
        # Keep only last 10 readings
        if len(self._cpu_readings) > 10:
            self._cpu_readings.pop(0)
        if len(self._memory_readings) > 10:
            self._memory_readings.pop(0)
        
        # Calculate request rate (requests per second)
        request_rate = self._calculate_request_rate()
        
        # Calculate average response time
        avg_response_time = self._calculate_avg_response_time()
        
        return ScalingMetricsSnapshot(
            timestamp=datetime.now(),
            cpu_utilization=cpu_percent,
            memory_utilization=memory_percent,
            request_rate=request_rate,
            average_response_time=avg_response_time,
            queue_depth=self._get_queue_depth(),
            active_connections=self._active_connections,
            current_replicas=self._get_current_replicas()
        )
    
    def _calculate_request_rate(self) -> float:
        """Calculate requests per second"""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        if elapsed > 0:
            return self._request_count / elapsed
        return 0.0
    
    def _calculate_avg_response_time(self) -> float:
        """Calculate average response time in milliseconds"""
        if not self._request_times:
            return 0.0
        return sum(self._request_times[-100:]) / len(self._request_times[-100:])
    
    def _get_queue_depth(self) -> int:
        """Get number of pending tasks in Celery queue"""
        try:
            from app.celery_config import app as celery_app
            inspector = celery_app.control.inspect()
            active = inspector.active()
            if active:
                return sum(len(tasks) for tasks in active.values())
        except Exception as e:
            logger.warning(f"Failed to get queue depth: {e}")
        return 0
    
    def _get_current_replicas(self) -> int:
        """Get current number of running replicas"""
        # This would be retrieved from Kubernetes API in production
        # For now, return 1 for single instance
        return 1
    
    def record_request(self, response_time_ms: float):
        """Record a request for metrics calculation"""
        self._request_count += 1
        self._request_times.append(response_time_ms)
    
    def increment_connections(self):
        """Increment active connection count"""
        self._active_connections += 1
    
    def decrement_connections(self):
        """Decrement active connection count"""
        self._active_connections = max(0, self._active_connections - 1)


class ScalingTestSuite:
    """Test scenarios for auto-scaling behavior"""
    
    @staticmethod
    def test_cpu_scale_up():
        """Test scaling up when CPU exceeds threshold"""
        manager = AutoScalingManager(ScalingPolicies.BALANCED)
        
        # Simulate high CPU usage
        for i in range(4):
            snapshot = ScalingMetricsSnapshot(
                timestamp=datetime.now(),
                cpu_utilization=75.0,  # Above 70% threshold
                memory_utilization=50.0,
                request_rate=1100.0,
                average_response_time=45.0,
                queue_depth=10,
                active_connections=150,
                current_replicas=3
            )
            trigger = manager.evaluate_metrics(snapshot)
            if trigger == ScalingTrigger.SCALE_UP:
                new_replicas = manager.calculate_replicas(trigger)
                manager.record_scaling_event(snapshot, trigger, new_replicas, 
                                            ScalingMetric.CPU, 75.0, "CPU exceeded 70%")
                return True
        
        return False
    
    @staticmethod
    def test_cpu_scale_down():
        """Test scaling down when CPU is low"""
        manager = AutoScalingManager(ScalingPolicies.BALANCED)
        manager.current_replicas = 10
        
        # Simulate low CPU usage
        for i in range(4):
            snapshot = ScalingMetricsSnapshot(
                timestamp=datetime.now(),
                cpu_utilization=30.0,  # Below 40% threshold
                memory_utilization=35.0,
                request_rate=150.0,
                average_response_time=20.0,
                queue_depth=0,
                active_connections=30,
                current_replicas=10
            )
            trigger = manager.evaluate_metrics(snapshot)
            if trigger == ScalingTrigger.SCALE_DOWN:
                new_replicas = manager.calculate_replicas(trigger)
                manager.record_scaling_event(snapshot, trigger, new_replicas,
                                            ScalingMetric.CPU, 30.0, "CPU below 40%")
                return True
        
        return False
    
    @staticmethod
    def test_policy_switching():
        """Test switching between policies"""
        # Start with conservative
        manager = AutoScalingManager(ScalingPolicies.CONSERVATIVE)
        assert manager.policy.name == "conservative"
        
        # Switch to aggressive for load spike
        manager.policy = ScalingPolicies.AGGRESSIVE
        assert manager.policy.name == "aggressive"
        
        # Verify new thresholds apply
        cpu_trigger = manager.policy.triggers[0]
        assert cpu_trigger.upper_bound == 60.0
        
        return True


# Flask integration helpers

def get_autoscaling_manager() -> AutoScalingManager:
    """Get or create the global auto-scaling manager"""
    if not hasattr(get_autoscaling_manager, '_instance'):
        get_autoscaling_manager._instance = AutoScalingManager()
    return get_autoscaling_manager._instance


def get_metrics_collector() -> MetricsCollector:
    """Get or create the global metrics collector"""
    if not hasattr(get_metrics_collector, '_instance'):
        get_metrics_collector._instance = MetricsCollector()
    return get_metrics_collector._instance


def evaluate_scaling() -> Dict:
    """Evaluate current state and return scaling recommendation"""
    collector = get_metrics_collector()
    manager = get_autoscaling_manager()
    
    snapshot = collector.collect_metrics()
    trigger = manager.evaluate_metrics(snapshot)
    
    return {
        "trigger": trigger.value,
        "current_replicas": manager.current_replicas,
        "metrics": {
            "cpu": snapshot.cpu_utilization,
            "memory": snapshot.memory_utilization,
            "request_rate": snapshot.request_rate,
            "response_time_ms": snapshot.average_response_time,
        }
    }


if __name__ == "__main__":
    # Run tests
    print("Testing auto-scaling behavior...")
    
    tests = [
        ("CPU Scale Up", ScalingTestSuite.test_cpu_scale_up),
        ("CPU Scale Down", ScalingTestSuite.test_cpu_scale_down),
        ("Policy Switching", ScalingTestSuite.test_policy_switching),
    ]
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{status}: {test_name}")
        except Exception as e:
            print(f"✗ ERROR: {test_name} - {e}")
    
    # Show example metrics
    print("\nExample scaling decisions:")
    collector = MetricsCollector()
    for i in range(3):
        snapshot = collector.collect_metrics()
        print(f"Snapshot {i+1}: CPU={snapshot.cpu_utilization:.1f}% "
              f"Memory={snapshot.memory_utilization:.1f}%")
