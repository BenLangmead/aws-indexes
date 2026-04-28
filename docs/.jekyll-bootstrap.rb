# frozen_string_literal: true

# Loaded before Jekyll via RUBYOPT (see README). The `github-pages` gem forces
# `safe: true`, so `_plugins/` never runs locally. Liquid 4.0.3 calls
# `Object#tainted?`, removed in Ruby 3.2+.
unless Object.method_defined?(:tainted?)
  class Object
    def tainted?
      false
    end

    def untaint
      self
    end
  end
end
