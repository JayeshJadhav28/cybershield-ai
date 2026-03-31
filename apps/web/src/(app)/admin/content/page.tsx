import { PageHeader } from '@/components/shared/page-header';
import { EmptyState } from '@/components/shared/empty-state';
import { Settings } from 'lucide-react';

export default function AdminContentPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Content Management"
        description="Manage quiz questions, scenarios, and awareness content."
        icon={Settings}
      />
      <EmptyState
        title="Coming in Phase 2"
        description="Content management tools for quiz questions and scenario editing will be available in a future release."
      />
    </div>
  );
}