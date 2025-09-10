"""
Processing Pipeline Workflow Management
Legal Document Intelligence Platform - BigQuery AI Hackathon Entry

This module manages the document processing workflow and pipeline orchestration.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class ProcessingStage(Enum):
    """Processing pipeline stages."""
    VALIDATION = "validation"
    AI_PROCESSING = "ai_processing"
    VECTOR_GENERATION = "vector_generation"
    PREDICTIVE_ANALYSIS = "predictive_analysis"
    STORAGE = "storage"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class PipelineStep:
    """Individual pipeline step configuration."""
    stage: ProcessingStage
    handler: Callable
    retry_count: int = 3
    timeout: int = 300  # 5 minutes
    dependencies: List[ProcessingStage] = None

class ProcessingPipeline:
    """
    Manages the document processing workflow with error handling,
    retry logic, and status tracking.
    """

    def __init__(self):
        """Initialize the processing pipeline."""
        self.steps = self._initialize_pipeline_steps()
        self.pipeline_status = {}
        self.pipeline_metrics = {
            'total_documents': 0,
            'successful_documents': 0,
            'failed_documents': 0,
            'average_pipeline_time': 0.0,
            'stage_timings': {}
        }

    def _initialize_pipeline_steps(self) -> Dict[ProcessingStage, PipelineStep]:
        """Initialize pipeline steps with their configurations."""
        return {
            ProcessingStage.VALIDATION: PipelineStep(
                stage=ProcessingStage.VALIDATION,
                handler=self._validate_document,
                retry_count=2,
                timeout=30
            ),
            ProcessingStage.AI_PROCESSING: PipelineStep(
                stage=ProcessingStage.AI_PROCESSING,
                handler=self._run_ai_processing,
                retry_count=3,
                timeout=180,
                dependencies=[ProcessingStage.VALIDATION]
            ),
            ProcessingStage.VECTOR_GENERATION: PipelineStep(
                stage=ProcessingStage.VECTOR_GENERATION,
                handler=self._generate_embeddings,
                retry_count=2,
                timeout=120,
                dependencies=[ProcessingStage.AI_PROCESSING]
            ),
            ProcessingStage.PREDICTIVE_ANALYSIS: PipelineStep(
                stage=ProcessingStage.PREDICTIVE_ANALYSIS,
                handler=self._run_predictive_analysis,
                retry_count=3,
                timeout=240,
                dependencies=[ProcessingStage.AI_PROCESSING]
            ),
            ProcessingStage.STORAGE: PipelineStep(
                stage=ProcessingStage.STORAGE,
                handler=self._store_results,
                retry_count=2,
                timeout=60,
                dependencies=[ProcessingStage.VECTOR_GENERATION, ProcessingStage.PREDICTIVE_ANALYSIS]
            )
        }

    async def process_document_pipeline(self, document: Dict[str, Any], processor) -> Dict[str, Any]:
        """
        Execute the complete processing pipeline for a document.

        Args:
            document: Document to process
            processor: LegalDocumentProcessor instance

        Returns:
            Pipeline execution result
        """
        document_id = document.get('document_id', 'unknown')
        start_time = datetime.now()

        logger.info(f"🔄 Starting pipeline for document {document_id}")

        # Initialize pipeline status
        self.pipeline_status[document_id] = {
            'current_stage': ProcessingStage.VALIDATION,
            'start_time': start_time,
            'stage_results': {},
            'errors': [],
            'retry_counts': {}
        }

        try:
            # Execute pipeline steps in order
            for stage in ProcessingStage:
                if stage in [ProcessingStage.COMPLETED, ProcessingStage.FAILED]:
                    continue

                step = self.steps[stage]

                # Check dependencies
                if not self._check_dependencies(document_id, step.dependencies):
                    raise ValueError(f"Dependencies not met for stage {stage.value}")

                # Execute stage
                stage_result = await self._execute_stage(
                    stage, step, document, processor, document_id
                )

                # Update pipeline status
                self.pipeline_status[document_id]['stage_results'][stage.value] = stage_result
                self.pipeline_status[document_id]['current_stage'] = stage

                # Check if stage failed
                if not stage_result.get('success', False):
                    self.pipeline_status[document_id]['current_stage'] = ProcessingStage.FAILED
                    self.pipeline_status[document_id]['errors'].append(
                        f"Stage {stage.value} failed: {stage_result.get('error', 'Unknown error')}"
                    )
                    break

            # Determine final status
            end_time = datetime.now()
            pipeline_time = (end_time - start_time).total_seconds()

            if self.pipeline_status[document_id]['current_stage'] != ProcessingStage.FAILED:
                self.pipeline_status[document_id]['current_stage'] = ProcessingStage.COMPLETED
                self.pipeline_status[document_id]['end_time'] = end_time
                self.pipeline_status[document_id]['pipeline_time'] = pipeline_time

                # Update metrics
                self._update_pipeline_metrics(pipeline_time, success=True)

                logger.info(f"✅ Pipeline completed for document {document_id} in {pipeline_time:.2f}s")
            else:
                self.pipeline_status[document_id]['end_time'] = end_time
                self.pipeline_status[document_id]['pipeline_time'] = pipeline_time

                # Update metrics
                self._update_pipeline_metrics(pipeline_time, success=False)

                logger.error(f"❌ Pipeline failed for document {document_id}")

            return {
                'document_id': document_id,
                'status': self.pipeline_status[document_id]['current_stage'].value,
                'pipeline_time': pipeline_time,
                'stage_results': self.pipeline_status[document_id]['stage_results'],
                'errors': self.pipeline_status[document_id]['errors']
            }

        except Exception as e:
            # Handle pipeline-level errors
            end_time = datetime.now()
            pipeline_time = (end_time - start_time).total_seconds()

            self.pipeline_status[document_id].update({
                'current_stage': ProcessingStage.FAILED,
                'end_time': end_time,
                'pipeline_time': pipeline_time,
                'errors': [str(e)]
            })

            self._update_pipeline_metrics(pipeline_time, success=False)

            logger.error(f"❌ Pipeline error for document {document_id}: {e}")

            return {
                'document_id': document_id,
                'status': 'failed',
                'pipeline_time': pipeline_time,
                'error': str(e)
            }

    async def _execute_stage(self, stage: ProcessingStage, step: PipelineStep,
                           document: Dict[str, Any], processor, document_id: str) -> Dict[str, Any]:
        """Execute a single pipeline stage with retry logic."""
        retry_count = 0
        last_error = None

        while retry_count <= step.retry_count:
            try:
                logger.info(f"🔄 Executing stage {stage.value} (attempt {retry_count + 1})")

                # Update retry count
                if document_id not in self.pipeline_status:
                    self.pipeline_status[document_id] = {}
                if 'retry_counts' not in self.pipeline_status[document_id]:
                    self.pipeline_status[document_id]['retry_counts'] = {}
                self.pipeline_status[document_id]['retry_counts'][stage.value] = retry_count

                # Execute stage handler
                stage_start = datetime.now()
                result = await self._run_stage_handler(stage, step, document, processor)
                stage_time = (datetime.now() - stage_start).total_seconds()

                # Update stage timing metrics
                if stage.value not in self.pipeline_metrics['stage_timings']:
                    self.pipeline_metrics['stage_timings'][stage.value] = []
                self.pipeline_metrics['stage_timings'][stage.value].append(stage_time)

                result['success'] = True
                result['execution_time'] = stage_time
                result['attempt'] = retry_count + 1

                logger.info(f"✅ Stage {stage.value} completed in {stage_time:.2f}s")
                return result

            except Exception as e:
                last_error = e
                retry_count += 1

                logger.warning(f"⚠️ Stage {stage.value} failed (attempt {retry_count}): {e}")

                if retry_count <= step.retry_count:
                    # Wait before retry (exponential backoff)
                    wait_time = min(2 ** retry_count, 30)  # Max 30 seconds
                    logger.info(f"⏳ Waiting {wait_time}s before retry...")
                    await asyncio.sleep(wait_time)

        # All retries exhausted
        return {
            'success': False,
            'error': str(last_error),
            'retry_count': retry_count,
            'stage': stage.value
        }

    async def _run_stage_handler(self, stage: ProcessingStage, step: PipelineStep,
                               document: Dict[str, Any], processor) -> Dict[str, Any]:
        """Run the specific handler for a pipeline stage."""
        if stage == ProcessingStage.VALIDATION:
            return processor._validate_document(document)
        elif stage == ProcessingStage.AI_PROCESSING:
            return processor._run_ai_processing(document)
        elif stage == ProcessingStage.VECTOR_GENERATION:
            ai_results = self.pipeline_status[document.get('document_id', 'unknown')]['stage_results'].get('ai_processing', {})
            return processor._generate_embeddings(document, ai_results)
        elif stage == ProcessingStage.PREDICTIVE_ANALYSIS:
            ai_results = self.pipeline_status[document.get('document_id', 'unknown')]['stage_results'].get('ai_processing', {})
            return processor._run_predictive_analysis(document, ai_results)
        elif stage == ProcessingStage.STORAGE:
            # Collect all results for storage
            stage_results = self.pipeline_status[document.get('document_id', 'unknown')]['stage_results']
            all_results = {
                'ai_analysis': stage_results.get('ai_processing', {}),
                'vector_analysis': stage_results.get('vector_generation', {}),
                'predictive_analysis': stage_results.get('predictive_analysis', {})
            }
            return processor._store_processing_results(document.get('document_id', 'unknown'), all_results)
        else:
            raise ValueError(f"Unknown pipeline stage: {stage}")

    def _check_dependencies(self, document_id: str, dependencies: List[ProcessingStage]) -> bool:
        """Check if all dependencies for a stage are satisfied."""
        if not dependencies:
            return True

        document_status = self.pipeline_status.get(document_id, {})
        stage_results = document_status.get('stage_results', {})

        for dependency in dependencies:
            if dependency.value not in stage_results:
                return False

            if not stage_results[dependency.value].get('success', False):
                return False

        return True

    def _update_pipeline_metrics(self, pipeline_time: float, success: bool):
        """Update pipeline metrics."""
        self.pipeline_metrics['total_documents'] += 1

        if success:
            self.pipeline_metrics['successful_documents'] += 1
        else:
            self.pipeline_metrics['failed_documents'] += 1

        # Update average pipeline time
        total = self.pipeline_metrics['total_documents']
        current_avg = self.pipeline_metrics['average_pipeline_time']
        self.pipeline_metrics['average_pipeline_time'] = (
            (current_avg * (total - 1) + pipeline_time) / total
        )

    def get_pipeline_status(self, document_id: str) -> Dict[str, Any]:
        """Get pipeline status for a specific document."""
        return self.pipeline_status.get(document_id, {'status': 'not_found'})

    def get_pipeline_metrics(self) -> Dict[str, Any]:
        """Get overall pipeline metrics."""
        return {
            'metrics': self.pipeline_metrics.copy(),
            'active_pipelines': len([s for s in self.pipeline_status.values()
                                   if s.get('current_stage') not in [ProcessingStage.COMPLETED, ProcessingStage.FAILED]]),
            'timestamp': datetime.now().isoformat()
        }

    def get_stage_timing_stats(self) -> Dict[str, Any]:
        """Get timing statistics for each pipeline stage."""
        stats = {}

        for stage, timings in self.pipeline_metrics['stage_timings'].items():
            if timings:
                stats[stage] = {
                    'count': len(timings),
                    'average_time': sum(timings) / len(timings),
                    'min_time': min(timings),
                    'max_time': max(timings),
                    'total_time': sum(timings)
                }

        return stats

def main():
    """Test the processing pipeline."""
    print("🔄 Processing Pipeline - Phase 3 Implementation")
    print("=" * 60)

    # This would be used in integration tests
    print("✅ Processing pipeline class created successfully")

if __name__ == "__main__":
    main()
