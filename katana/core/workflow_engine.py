import time
import logging
import yaml
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class WorkflowEngine:
    """Executes automated game workflows using pure computer vision"""
    
    def __init__(self, settings_path="config/settings.yaml"):
        """Initialize workflow engine with components"""
        from katana.core.game_controller import GameController
        from katana.core.input_simulator import InputSimulator
        from katana.core.screen_analyzer import ScreenAnalyzer
        
        # Load settings
        with open(settings_path, 'r') as f:
            self.settings = yaml.safe_load(f)
        
        # Initialize components
        self.game_controller = GameController(settings_path)
        self.input_simulator = InputSimulator(settings_path)
        self.screen_analyzer = ScreenAnalyzer(settings_path)
        self.screen_analyzer.workflow_engine = self
        
        self.current_game = None
        self.default_timeout = self.settings.get('timeout', 300)
        self.workflow_running = False
        self.workflow_results = []
        
        # Timing tracking for benchmarks
        self.timing_markers = {}
    
    def run_workflow(self, game_config):
        """Run a workflow for the specified game"""
        self.current_game = game_config
        self.workflow_running = True
        self.workflow_results = []
        self.timing_markers = {}  # Reset timing markers
        
        workflow = game_config['config'].get('workflow', [])
        
        if not workflow:
            logger.warning(f"No workflow defined for {game_config['config']['name']}")
            return False
        
        logger.info(f"Starting workflow for {game_config['config']['name']}")
        logger.info(f"Workflow has {len(workflow)} steps")
        
        try:
            # Execute each step in the workflow
            for i, step in enumerate(workflow):
                if not self.workflow_running:
                    logger.info("Workflow stopped by user")
                    return False
                
                step_name = step.get('action', f'step_{i+1}')
                logger.info(f"Executing workflow step {i+1}/{len(workflow)}: {step_name}")
                
                success = self._execute_step(step, game_config)
                
                # Record step result
                self.workflow_results.append({
                    'step': i+1,
                    'action': step_name,
                    'success': success,
                    'timestamp': time.time()
                })
                
                if not success:
                    logger.error(f"Workflow step {i+1} failed: {step_name}")
                    
                    # Check if this step is marked as optional
                    if not step.get('optional', False):
                        logger.error("Step is not optional, stopping workflow")
                        return False
                    else:
                        logger.warning("Step is optional, continuing workflow")
                        continue
                
                # Add delay between steps if specified
                step_delay = step.get('step_delay', 0)
                if step_delay > 0:
                    logger.debug(f"Step delay: {step_delay}s")
                    time.sleep(step_delay)
            
            # Log final timing summary if we have timing markers
            self._log_timing_summary()
            
            logger.info(f"Workflow completed successfully for {game_config['config']['name']}")
            return True
            
        except Exception as e:
            logger.error(f"Workflow failed with exception: {str(e)}")
            return False
        finally:
            self.workflow_running = False
    
    def stop_workflow(self):
        """Stop the currently running workflow"""
        self.workflow_running = False
        logger.info("Workflow stop requested")
    
    def get_workflow_status(self):
        """Get current workflow status"""
        return {
            'running': self.workflow_running,
            'current_game': self.current_game['config']['name'] if self.current_game else None,
            'results': self.workflow_results,
            'timing_markers': self.timing_markers
        }
    
    def _execute_step(self, step, game_config):
        """Execute a single workflow step"""
        action = step['action']
        
        try:
            # Handle different action types
            if action == 'launch_game':
                return self._action_launch_game(step, game_config)
            
            elif action == 'wait_for_game':
                return self._action_wait_for_game(step, game_config)
            
            elif action == 'exit_game':
                return self._action_exit_game(step, game_config)
            
            elif action == 'wait_for_template':
                return self._action_wait_for_template(step, game_config)
            
            elif action == 'wait_for_any_template':
                return self._action_wait_for_any_template(step, game_config)
            
            elif action == 'wait_for_template_disappear':
                return self._action_wait_for_template_disappear(step, game_config)
            
            elif action == 'click_template':
                return self._action_click_template(step, game_config)
            
            elif action == 'click_template_if_exists':
                return self._action_click_template_if_exists(step, game_config)
            
            elif action == 'wait_for_screen_change':
                return self._action_wait_for_screen_change(step, game_config)
            
            elif action == 'press_key':
                return self._action_press_key(step, game_config)
            
            elif action == 'hold_key':
                return self._action_hold_key(step, game_config)
            
            elif action == 'type_text':
                return self._action_type_text(step, game_config)
            
            elif action == 'click':
                return self._action_click(step, game_config)
            
            elif action == 'take_screenshot':
                return self._action_take_screenshot(step, game_config)
            
            elif action == 'wait':
                return self._action_wait(step, game_config)
            
            elif action == 'check_template':
                return self._action_check_template(step, game_config)
            
            elif action == 'retry_action':
                return self._action_retry(step, game_config)
            
            elif action == 'log_message':
                return self._action_log_message(step, game_config)
            
            else:
                logger.error(f"Unknown action: {action}")
                return False
                
        except Exception as e:
            logger.error(f"Error executing action {action}: {str(e)}")
            return False
    
    def _action_launch_game(self, step, game_config):
        """Launch the game"""
        try:
            process = self.game_controller.launch_game(game_config)
            if process:
                logger.info(f"Game launch initiated: {game_config['config']['name']}")
                # Add this line:
                game_process = game_config['config'].get('process_name')
                self.screen_analyzer.set_current_game(game_process)
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to launch game: {str(e)}")
            return False
    
    def _action_wait_for_game(self, step, game_config):
        """Wait for game to start"""
        timeout = step.get('timeout', self.default_timeout)
        process_name = step.get('process_name', game_config['config'].get('process_name'))
        
        return self.game_controller.wait_for_game_to_start(timeout, process_name)
    
    def _action_exit_game(self, step, game_config):
        """Exit the game"""
        force = step.get('force', False)
        process_name = step.get('process_name', game_config['config'].get('process_name'))
        
        return self.game_controller.close_game(process_name, force=force)
    
    def _action_wait_for_template(self, step, game_config):
        """Wait for a template to appear"""
        template_path = step.get('template')
        timeout = step.get('timeout', self.default_timeout)
        region = step.get('region')
        threshold = step.get('threshold')
        
        if not template_path:
            logger.error("No template specified for 'wait_for_template' action")
            return False
        
        # Resolve template path
        template_path = self._resolve_template_path(template_path, game_config)
        
        matched, location = self.screen_analyzer.wait_for_template(
            template_path, timeout=timeout, region=region, threshold=threshold
        )
        
        if matched:
            logger.info(f"Template found: {template_path}")
        else:
            logger.warning(f"Template not found within timeout: {template_path}")
        
        return matched
    
    def _action_wait_for_any_template(self, step, game_config):
        """Wait for any of multiple templates to appear"""
        templates = step.get('templates', [])
        timeout = step.get('timeout', self.default_timeout)
        region = step.get('region')
        threshold = step.get('threshold')
        
        if not templates:
            logger.error("No templates specified for 'wait_for_any_template' action")
            return False
        
        # Resolve template paths
        template_paths = [self._resolve_template_path(t, game_config) for t in templates]
        
        matched, result = self.screen_analyzer.wait_for_any_template(
            template_paths, timeout=timeout, region=region, threshold=threshold
        )
        
        if matched:
            template_path, location = result
            logger.info(f"Template found: {template_path}")
        else:
            logger.warning(f"No templates found within timeout: {templates}")
        
        return matched
    
    def _action_wait_for_template_disappear(self, step, game_config):
        """Wait for a template to disappear"""
        template_path = step.get('template')
        timeout = step.get('timeout', self.default_timeout)
        region = step.get('region')
        threshold = step.get('threshold')
        
        if not template_path:
            logger.error("No template specified for 'wait_for_template_disappear' action")
            return False
        
        # Resolve template path
        template_path = self._resolve_template_path(template_path, game_config)
        
        logger.info(f"Waiting for template to disappear: {template_path}")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            if not self.workflow_running:
                return False
            
            matched, _ = self.screen_analyzer.match_template(
                template_path, region=region, threshold=threshold
            )
            
            if not matched:
                logger.info(f"Template disappeared: {template_path}")
                return True
            
            time.sleep(0.5)
        
        logger.warning(f"Timeout waiting for template to disappear: {template_path}")
        return False
    
    def _action_click_template(self, step, game_config):
        """Find and click a template with enhanced timing control"""
        template_path = step.get('template')
        timeout = step.get('timeout', 10)
        region = step.get('region')
        threshold = step.get('threshold')
        button = step.get('button', 'left')
        click_offset = step.get('offset', (0, 0))
        
        # Enhanced timing controls
        move_duration = step.get('move_duration', 0.5)  # Time to move mouse
        pre_click_delay = step.get('pre_click_delay', 0.3)  # Delay before click
        post_click_delay = step.get('post_click_delay', 0.5)  # Delay after click
        
        if not template_path:
            logger.error("No template specified for 'click_template' action")
            return False
        
        # Resolve template path
        template_path = self._resolve_template_path(template_path, game_config)
        
        # Wait for template to appear
        matched, location = self.screen_analyzer.wait_for_template(
            template_path, timeout=timeout, region=region, threshold=threshold
        )
        
        if not matched:
            logger.error(f"Template not found for click: {template_path}")
            return False
        
        # Apply click offset
        x, y = location
        x += click_offset[0]
        y += click_offset[1]
        
        # Click at the template location with enhanced timing
        success = self.input_simulator.mouse_click(
            x, y, button, 
            move_duration=move_duration,
            pre_click_delay=pre_click_delay,
            post_click_delay=post_click_delay
        )
        
        if success:
            logger.info(f"✅ Clicked template: {template_path} at ({x}, {y})")
        else:
            logger.error(f"❌ Failed to click template: {template_path}")
        
        return success
    
    def _action_click_template_if_exists(self, step, game_config):
        """Click a template if it exists (non-blocking)"""
        template_path = step.get('template')
        region = step.get('region')
        threshold = step.get('threshold')
        button = step.get('button', 'left')
        delay = step.get('delay')
        click_offset = step.get('offset', (0, 0))
        
        if not template_path:
            logger.error("No template specified for 'click_template_if_exists' action")
            return False
        
        # Resolve template path
        template_path = self._resolve_template_path(template_path, game_config)
        
        # Check if template exists (no waiting)
        matched, location = self.screen_analyzer.match_template(
            template_path, region=region, threshold=threshold
        )
        
        if matched:
            # Apply click offset
            x, y = location
            x += click_offset[0]
            y += click_offset[1]
            
            # Click at the template location
            self.input_simulator.mouse_click(x, y, button, delay)
            logger.info(f"Clicked optional template: {template_path} at ({x}, {y})")
        else:
            logger.info(f"Optional template not found (skipping): {template_path}")
        
        return True  # Always return True for optional clicks
    
    def _action_wait_for_screen_change(self, step, game_config):
        """Wait for the screen to change"""
        timeout = step.get('timeout', self.default_timeout)
        region = step.get('region')
        threshold = step.get('threshold', 0.95)
        
        return self.screen_analyzer.wait_for_screen_change(timeout, region, threshold)
    
    def _action_press_key(self, step, game_config):
        """Press a keyboard key"""
        key = step.get('key')
        delay = step.get('delay')
        
        if not key:
            logger.error("No key specified for 'press_key' action")
            return False
        
        self.input_simulator.press_key(key, delay)
        return True
    
    def _action_hold_key(self, step, game_config):
        """Hold a keyboard key"""
        key = step.get('key')
        duration = step.get('duration', 1.0)
        
        if not key:
            logger.error("No key specified for 'hold_key' action")
            return False
        
        self.input_simulator.hold_key(key, duration)
        return True
    
    def _action_type_text(self, step, game_config):
        """Type text"""
        text = step.get('text')
        delay = step.get('delay')
        
        if not text:
            logger.error("No text specified for 'type_text' action")
            return False
        
        self.input_simulator.type_text(text, delay)
        return True
    
    def _action_click(self, step, game_config):
        """Click at specific coordinates"""
        x = step.get('x')
        y = step.get('y')
        button = step.get('button', 'left')
        delay = step.get('delay')
        
        if x is None or y is None:
            logger.error("No coordinates specified for 'click' action")
            return False
        
        self.input_simulator.mouse_click(x, y, button, delay)
        return True
    
    def _action_take_screenshot(self, step, game_config):
        """Take a screenshot"""
        try:
            name = step.get('name')
            region = step.get('region')
            
            if name:
                # Add timestamp to make filename unique
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                name = f"{name}_{timestamp}"
            
            path = self.screen_analyzer.save_screenshot(name)
            
            if path:
                logger.info(f"Screenshot taken: {path}")
                return True
            else:
                logger.error("Failed to save screenshot")
                return False
                
        except Exception as e:
            logger.error(f"Error taking screenshot: {e}")
            return False
    
    def _action_wait(self, step, game_config):
        """Wait for a specified time"""
        seconds = step.get('seconds', 1)
        logger.info(f"Waiting for {seconds} seconds")
        
        # Sleep in small chunks to allow workflow stopping
        elapsed = 0
        while elapsed < seconds and self.workflow_running:
            sleep_time = min(0.1, seconds - elapsed)
            time.sleep(sleep_time)
            elapsed += sleep_time
        
        return True
    
    def _action_check_template(self, step, game_config):
        """Check if a template exists (for conditional logic)"""
        template_path = step.get('template')
        region = step.get('region')
        threshold = step.get('threshold')
        
        if not template_path:
            logger.error("No template specified for 'check_template' action")
            return False
        
        # Resolve template path
        template_path = self._resolve_template_path(template_path, game_config)
        
        # Check if template exists
        matched, location = self.screen_analyzer.match_template(
            template_path, region=region, threshold=threshold
        )
        
        logger.info(f"Template check: {template_path} - {'Found' if matched else 'Not found'}")
        
        return matched
    
    def _action_retry(self, step, game_config):
        """Retry a sub-action multiple times"""
        sub_action = step.get('action_to_retry')
        max_retries = step.get('max_retries', 3)
        retry_delay = step.get('retry_delay', 1)
        
        if not sub_action:
            logger.error("No action_to_retry specified for 'retry_action'")
            return False
        
        for attempt in range(max_retries + 1):
            if not self.workflow_running:
                return False
            
            if attempt > 0:
                logger.info(f"Retry attempt {attempt}/{max_retries} for action: {sub_action['action']}")
                time.sleep(retry_delay)
            
            success = self._execute_step(sub_action, game_config)
            if success:
                return True
        
        logger.error(f"Action failed after {max_retries + 1} attempts: {sub_action['action']}")
        return False
    
    def _action_log_message(self, step, game_config):
        """Log a message with timestamp for timing measurement"""
        message = step.get('message', 'LOG_MESSAGE')
        timestamp = time.time()
        
        # Store timing marker for later analysis
        self.timing_markers[message] = timestamp
        
        # Log with special formatting for easy parsing
        logger.info(f"TIMING_MARKER: {message} at {timestamp:.6f} ({time.strftime('%H:%M:%S', time.localtime(timestamp))})")
        
        return True
    
    def _log_timing_summary(self):
        """Log a summary of timing markers if benchmark timing was measured"""
        if 'BENCHMARK_START_TIME' in self.timing_markers and 'BENCHMARK_END_TIME' in self.timing_markers:
            start_time = self.timing_markers['BENCHMARK_START_TIME']
            end_time = self.timing_markers['BENCHMARK_END_TIME']
            duration = end_time - start_time
            
            logger.info("=" * 60)
            logger.info("BENCHMARK TIMING SUMMARY")
            logger.info("=" * 60)
            
            # Fixed formatting - removed %f and added None checks
            try:
                start_str = time.strftime('%H:%M:%S', time.localtime(start_time))
                end_str = time.strftime('%H:%M:%S', time.localtime(end_time))
                
                logger.info(f">>>> Benchmark Start:     {start_str}")
                logger.info(f">>>> Benchmark End:       {end_str}")
                logger.info(f">>>> Total Duration:      {duration:.2f} seconds ({duration/60:.1f} minutes)")
            except Exception as e:
                logger.error(f"Error formatting timing: {e}")
                logger.info(f">>>> Benchmark Start:     {start_time}")
                logger.info(f">>>> Benchmark End:       {end_time}")
                logger.info(f">>>> Total Duration:      {duration} seconds")
            
            logger.info("=" * 60)
            
            # Log for automated parsing - with None check
            try:
                logger.info(f"BENCHMARK_DURATION: {duration:.6f}")
            except:
                logger.info(f"BENCHMARK_DURATION: {duration}")

    def get_benchmark_duration(self):
        """Get the benchmark duration if timing markers are available"""
        if 'BENCHMARK_START_TIME' in self.timing_markers and 'BENCHMARK_END_TIME' in self.timing_markers:
            return self.timing_markers['BENCHMARK_END_TIME'] - self.timing_markers['BENCHMARK_START_TIME']
        return None
    
    def _resolve_template_path(self, template_path, game_config):
        """Resolve template path relative to game or global templates"""
        if Path(template_path).is_absolute() or template_path.startswith('templates/'):
            return template_path
        
        # Try game-specific template first
        game_name = game_config['config']['name'].lower().replace(' ', '_')
        game_template = f"templates/screens/{game_name}/{template_path}"
        
        if Path(game_template).exists():
            return game_template
        
        # Fall back to global template
        global_template = f"templates/screens/{template_path}"
        return global_template
    
    def validate_workflow(self, game_config):
        """Validate a workflow configuration"""
        workflow = game_config['config'].get('workflow', [])
        errors = []
        warnings = []
        
        if not workflow:
            errors.append("No workflow defined")
            return errors, warnings
        
        for i, step in enumerate(workflow):
            step_num = i + 1
            action = step.get('action')
            
            if not action:
                errors.append(f"Step {step_num}: No action specified")
                continue
            
            # Validate action-specific requirements
            if action in ['wait_for_template', 'click_template', 'wait_for_template_disappear']:
                template = step.get('template')
                if not template:
                    errors.append(f"Step {step_num}: No template specified for {action}")
                else:
                    template_path = self._resolve_template_path(template, game_config)
                    if not Path(template_path).exists():
                        warnings.append(f"Step {step_num}: Template not found: {template_path}")
            
            elif action in ['press_key', 'hold_key']:
                if not step.get('key'):
                    errors.append(f"Step {step_num}: No key specified for {action}")
            
            elif action == 'type_text':
                if not step.get('text'):
                    errors.append(f"Step {step_num}: No text specified for {action}")
            
            elif action == 'click':
                if step.get('x') is None or step.get('y') is None:
                    errors.append(f"Step {step_num}: No coordinates specified for {action}")
            
            elif action == 'wait':
                if step.get('seconds') is None:
                    warnings.append(f"Step {step_num}: No duration specified for wait, using default 1s")
            
            elif action == 'log_message':
                if not step.get('message'):
                    warnings.append(f"Step {step_num}: No message specified for log_message, using default")
        
        return errors, warnings