import { PageHeader } from "@/components/shared/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ExternalLink, Phone, Shield } from "lucide-react";
import { EXTERNAL_LINKS } from "@/lib/constants";

export default function HelpPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Help & Support"
        description="Get help using CyberShield AI and find important cyber safety resources."
      />

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card className="border-cs-cyan/20">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-base">
              <Shield className="h-5 w-5 text-cs-cyan" />
              Report Cyber Crime
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm text-muted-foreground">
            <p>
              Report any cyber crime at the National Cyber Crime Reporting Portal.
            </p>
            <a
              href={EXTERNAL_LINKS.cyberCrimePortal}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 text-cs-cyan hover:underline"
            >
              cybercrime.gov.in <ExternalLink className="h-3.5 w-3.5" />
            </a>
          </CardContent>
        </Card>

        <Card className="border-cs-suspicious/20">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-base">
              <Phone className="h-5 w-5 text-cs-suspicious" />
              Emergency Helpline
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm text-muted-foreground">
            <p>For urgent cyber fraud cases, call the national helpline:</p>
            <p className="text-2xl font-bold text-foreground font-mono">
              {EXTERNAL_LINKS.cyberCrimeHelpline}
            </p>
          </CardContent>
        </Card>

        <Card className="border-cs-purple/20">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-base">
              <ExternalLink className="h-5 w-5 text-cs-purple" />
              CERT-In Advisories
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm text-muted-foreground">
            <p>Stay updated with the latest security advisories from CERT-In.</p>
            <a
              href={EXTERNAL_LINKS.certIn}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 text-cs-purple hover:underline"
            >
              cert-in.org.in <ExternalLink className="h-3.5 w-3.5" />
            </a>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}